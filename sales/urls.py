from django.urls import path
from .views import AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView, DashboardView, set_timezone
from . import views 

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('ads/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/new/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:ad_id>/update/', AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:ad_id>/delete/', AdDeleteView.as_view(), name='ad_delete'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("set-timezone/", views.set_timezone, name="set_timezone"),
]
