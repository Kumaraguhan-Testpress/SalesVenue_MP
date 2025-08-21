from django import forms
from django.forms import inlineformset_factory
from .models import Ad, AdImage, Message, Category

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
        if self.instance is None or self.instance.pk is None:
            first_category = Category.objects.first()
            if first_category:
                self.fields["category"].initial = first_category

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
