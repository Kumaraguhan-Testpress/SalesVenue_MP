from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from sales.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'email']

class CustomAuthenticationForm(AuthenticationForm):
    pass

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'profile_picture', 'contact_info_visibility']

