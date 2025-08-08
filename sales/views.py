from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Ad
from django.contrib.auth.mixins import LoginRequiredMixin

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
