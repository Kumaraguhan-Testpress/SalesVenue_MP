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
        # labels = {
        #     'username': 'Username',
        #     'email': 'Email',
        #     'phone_number': 'Phone Number',
        #     'profile_picture': 'Profile Picture',
        #     'contact_info_visibility': 'Show Contact Info Publicly',
        # }
