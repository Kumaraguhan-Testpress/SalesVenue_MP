from django import forms
from django.forms import inlineformset_factory
from .models import Ad, AdImage, Message

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            'title', 'description', 'price', 'location',
            'contact_info', 'contact_info_visible',
            'category', 'event_date'
        ]

class AdImageForm(forms.ModelForm):
    class Meta:
        model = AdImage
        fields = ['image']

AdImageFormSet = inlineformset_factory(
    Ad,
    AdImage,
    form=AdImageForm,
    extra=3,
    can_delete=True
)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
