from django.urls import path
from .views import AdListView, AdDetailView

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('ads/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
]
