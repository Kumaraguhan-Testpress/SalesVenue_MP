from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Ad, Conversation, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import AdForm, AdImageFormSet, MessageForm
from .mixins import AdOwnerRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q, Case, When, F
from django.utils.dateparse import parse_datetime

class AdListView(ListView):
    model = Ad
    template_name = 'ad_list_view.html'
    context_object_name = 'ads'
    
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # If not authenticated, render a different template with a welcome message
            return render(request, 'welcome.html')

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related('user', 'category') \
                                                .prefetch_related('images') \
                                                .order_by('-created_at')

class AdDetailView(LoginRequiredMixin ,DetailView):
    model = Ad
    template_name = 'ad_detail_view.html'
    context_object_name = 'ad'

    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related('user').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object
        user = self.request.user
        context['show_contact_info'] = ad.is_visible_to_user(user)
        
        ad_owner = ad.user
        context['show_user_contact_info'] = ad_owner.contact_info_visibility
        context['user_phone_number'] = ad_owner.phone_number if ad_owner.contact_info_visibility else None
        context['images'] = ad.images.all()

        return context

class AdImageFormsetMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['images_formset'] = AdImageFormSet(
                self.request.POST, self.request.FILES, instance=getattr(self, 'object', None)
            )
        else:
            context['images_formset'] = AdImageFormSet(instance=getattr(self, 'object', None))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']
        if images_formset.is_valid():
            self.object = form.save()
            images_formset.instance = self.object
            images_formset.save()
            messages.success(self.request, self.success_message)
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(form=form))

class AdCreateView(LoginRequiredMixin, AdImageFormsetMixin, CreateView):
    model = Ad
    template_name = 'ad_form.html'
    form_class = AdForm
    success_message = "Ad created successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AdUpdateView(LoginRequiredMixin, AdOwnerRequiredMixin, AdImageFormsetMixin, UpdateView):
    model = Ad
    template_name = 'ad_form.html'
    form_class = AdForm
    pk_url_kwarg = 'ad_id'
    success_message = "Ad updated successfully!"

class AdDeleteView(LoginRequiredMixin, AdOwnerRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ad_confirm_delete.html'
    pk_url_kwarg = 'ad_id'
    success_url = reverse_lazy('ad_list')

class StartConversationView(LoginRequiredMixin, View):
    def get(self, request, ad_id, *args, **kwargs):
        ad = get_object_or_404(Ad, pk=ad_id, is_active=True)
        owner = ad.user
        buyer = request.user

        if owner == buyer:
            # Owner should go to their own conversations list
            return redirect('conversation_list_for_ad', ad_id=ad.id)

        conversation, created = Conversation.objects.get_or_create(
            ad=ad,
            owner=owner,
            buyer=buyer
        )
        return redirect('conversation_detail', pk=conversation.pk)


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'conversations/list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        user = self.request.user
        conversations = (
            Conversation.objects
            .filter(Q(ad__user=user) | Q(buyer=user))
            .select_related('ad', 'buyer', 'ad__user')
            .annotate(
                other_username=Case(
                    When(ad__user=user, then=F('buyer__username')),
                    default=F('ad__user__username'),
                )
            )
            .order_by('-created_at')
        )
        return conversations

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'conversations/detail.html'
    context_object_name = 'conversation'
    pk_url_kwarg = 'conversation_id'

    def dispatch(self, request, *args, **kwargs):
        conversation = self.get_object()
        if request.user not in (conversation.owner, conversation.buyer):
            return HttpResponseForbidden("You don't have access to this conversation.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.object
        context['messages'] = conversation.messages.select_related('sender').all()
        context['form'] = MessageForm()
        context["other_user"] = conversation.other_user(self.request.user)
        return context


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, conversation_id, *args, **kwargs):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if request.user not in (conversation.owner, conversation.buyer):
            return JsonResponse({'error': 'forbidden'}, status=403)

        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.sent_at = timezone.now()
            msg.save()
            return JsonResponse({
                'id': msg.pk,
                'sender': msg.sender.username,
                'content': msg.content,
                'sent_at': msg.sent_at.isoformat(),
            })
        return JsonResponse({'errors': form.errors}, status=400)


class ConversationMessagesJSONView(LoginRequiredMixin, View):
    def get(self, request, conversation_id, *args, **kwargs):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if request.user not in (conversation.owner, conversation.buyer):
            return JsonResponse({'error': 'forbidden'}, status=403)

        after = request.GET.get('after')
        qs = conversation.messages.select_related('sender').all()
        if after:
            dt = parse_datetime(after)
            if dt:
                qs = qs.filter(sent_at__gt=dt)

        data = [{
            'id': m.pk,
            'sender': m.sender.username,
            'sender_id': m.sender_id,
            'content': m.content,
            'sent_at': m.sent_at.isoformat(),
            'read': m.read
        } for m in qs]
        return JsonResponse({'messages': data})


class AdConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'conversations/ad_conversations.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        ad_id = self.kwargs['ad_id']
        self.ad = get_object_or_404(Ad, pk=ad_id)
        if self.ad.user != self.request.user:
            return Conversation.objects.none()  # or raise 403
        return self.ad.conversations.select_related('buyer').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad'] = self.ad
        return context
