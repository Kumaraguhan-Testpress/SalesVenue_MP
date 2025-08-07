from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from sales.models import Ad, Category, CustomUser, AdImage

class AdListViewTests(TestCase):
    def setUp(self):
        """
        Set up test data for all test methods.

        Creates a user, a category, two active ads, one inactive ad,
        and an image associated with one of the active ads.
        """

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
        """ Test that the ad list view returns a 200 OK status code. """

        response = self.client.get(reverse('ad_list'))  # Change 'ad-list' to your actual URL name
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        """ Test that the ad list view uses the correct template. """

        response = self.client.get(reverse('ad_list'))
        self.assertTemplateUsed(response, 'ad_list_view.html')

    def test_only_active_ads_displayed(self):
        """ Test that the view context only contains active ads. """

        response = self.client.get(reverse('ad_list'))
        ads = response.context['ads']
        self.assertIn(self.active_ad1, ads)
        self.assertIn(self.active_ad2, ads)
        self.assertNotIn(self.inactive_ad, ads)
        self.assertEqual(len(ads), 2)

    def test_ad_data_rendered_in_template(self):
        """
        Test that the details of an active ad are correctly rendered in the template.
        """

        response = self.client.get(reverse('ad_list'))
        content = response.content.decode()

        self.assertIn(self.active_ad1.title, content)
        self.assertIn(self.active_ad1.category.name, content)
        self.assertIn(str(self.active_ad1.price), content)
        self.assertIn(self.active_ad1.location, content)
        self.assertIn(self.user.username, content)

    def test_image_is_rendered(self):
        """
        Test that the image URL for an ad with an image is present in the response content.
        """

        response = self.client.get(reverse('ad_list'))
        self.assertContains(response, 'ad_images/')

    def test_empty_ad_list(self):
        """ Test that the correct message is displayed when there are no active ads. """

        Ad.objects.all().delete()
        response = self.client.get(reverse('ad_list'))
        self.assertContains(response, 'No ads are currently available.')

    def test_pagination_is_working(self):
        """
        Test that pagination limits the number of ads displayed per page
        and that subsequent pages are accessible.
        """

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
