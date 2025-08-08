from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserUpdateForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView,UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from sales.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    template_name = 'logout.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
