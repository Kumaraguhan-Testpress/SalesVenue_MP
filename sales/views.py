from django.shortcuts import render
from django.views.generic import ListView
from .models import Ad

class AdListView(ListView):
    model = Ad
    template_name = 'AdListView.html'
    context_object_name = 'ads'
    
    paginate_by = 10
    
    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related('user', 'category') \
                                                .prefetch_related('images') \
                                                .order_by('-created_at')
