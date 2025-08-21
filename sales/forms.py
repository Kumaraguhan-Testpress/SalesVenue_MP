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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If no instance is passed (new Ad), set default category
        if not self.instance.pk and Category.objects.exists():
            self.fields['category'].initial = Category.objects.first()

class AdImageForm(forms.ModelForm):
    class Meta:
        model = AdImage
        fields = ['image']

AdImageFormSet = inlineformset_factory(
    Ad,
    AdImage,
    form=AdImageForm,
    extra=1,
    can_delete=True
)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
