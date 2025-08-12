from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from sales.models import Ad, Category, CustomUser, AdImage

class AdListViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category')

        self.active_ad1 = Ad.objects.create(
            user=self.user,
            title='Active Ad 1',
            description='Description 1',
            price=100.00,
            location='Location 1',
            contact_info='contact1@example.com',
            category=self.category,
            is_active=True
        )
        self.active_ad2 = Ad.objects.create(
            user=self.user,
            title='Active Ad 2',
            description='Description 2',
            price=200.00,
            location='Location 2',
            contact_info='contact2@example.com',
            category=self.category,
            is_active=True
        )
        self.inactive_ad = Ad.objects.create(
            user=self.user,
            title='Inactive Ad',
            description='Description Inactive',
            price=300.00,
            location='Location Inactive',
            contact_info='contact3@example.com',
            category=self.category,
            is_active=False
        )

        self.image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        AdImage.objects.create(ad=self.active_ad1, image=self.image)

    def test_view_status_code(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse('ad_list'))
        self.assertTemplateUsed(response, 'welcome.html')

    def test_only_active_ads_displayed(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ad_list'))
        ads = response.context['ads']
        self.assertIn(self.active_ad1, ads)
        self.assertIn(self.active_ad2, ads)
        self.assertNotIn(self.inactive_ad, ads)
        self.assertEqual(len(ads), 2)

    def test_empty_ad_list(self):
        self.client.force_login(self.user)
        Ad.objects.all().delete()
        response = self.client.get(reverse('ad_list'))
        self.assertContains(response, 'No ads are currently available.')

    def test_pagination_is_working(self):
        self.client.force_login(self.user)
        for i in range(11):
            Ad.objects.create(
                user=self.user,
                title=f'Paginated Ad {i}',
                description='...',
                price=10 + i,
                location='X',
                contact_info='test@example.com',
                category=self.category,
                is_active=True
            )
        response = self.client.get(reverse('ad_list'))
        ads = response.context['ads']
        self.assertEqual(len(ads), 10)  # paginate_by = 10

        response = self.client.get(reverse('ad_list') + '?page=2')
        self.assertEqual(response.context['page_obj'].number, 2)
