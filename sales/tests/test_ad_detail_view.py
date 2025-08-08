from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from sales.models import Ad, AdImage, Category
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

class AdDetailViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.user = User.objects.create_user(username='testuser', password='password')
        self.ad_owner = User.objects.create_user(username='owner', password='password', first_name='OwnerName')
        self.ad_owner.phone_number = '1234567890'
        self.ad_owner.contact_info_visibility = True
        self.ad_owner.save()

        self.category = Category.objects.create(name='Electronics')

        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Test Description',
            price=100,
            location='Test City',
            user=self.ad_owner,
            is_active=True,
            category=self.category,
            created_at=date.today(),
            event_date=date(2025, 9, 1),
            contact_info='owner@example.com'
        )

        self.image = AdImage.objects.create(ad=self.ad, image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'))
        self.detail_url = reverse('ad_detail', kwargs={'pk': self.ad.pk})

    def test_ad_detail_view_renders_active_ad(self):
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)

    def test_only_active_ads_are_accessible(self):
        self.ad.is_active = False
        self.ad.save()
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_context_includes_contact_info_visibility(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.detail_url)
        self.assertIn('show_contact_info', response.context)
        self.assertIn('show_user_contact_info', response.context)

    def test_user_contact_info_shown_when_visible(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Seller Contact')
        self.assertContains(response, '1234567890')

    def test_user_contact_info_hidden_when_not_visible(self):
        self.ad_owner.contact_info_visibility = False
        self.ad_owner.save()
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, 'Seller Contact')
        self.assertNotContains(response, '1234567890')

    def test_images_are_included_in_context(self):
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertIn('images', response.context)
        self.assertEqual(list(response.context['images']), list(self.ad.images.all()))
        self.assertContains(response, self.image.image.url)

    def test_template_used(self):
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertTemplateUsed(response, 'ad_detail_view.html')

    def test_event_date_displayed(self):
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertContains(response, self.ad.event_date.strftime('%B %d, %Y'))

    def test_ad_owner_username_displayed(self):
        self.client.force_login(self.ad_owner)
        response = self.client.get(self.ad.get_absolute_url())
        self.assertContains(response, self.ad_owner.username)

    def test_contact_info_hidden_if_not_visible_to_user(self):        
        self.ad.contact_info_visibility = False
        self.ad.save()
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Ad contact information is hidden.')