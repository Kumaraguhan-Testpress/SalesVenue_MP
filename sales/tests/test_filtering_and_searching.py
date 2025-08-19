from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Ad, Category
from datetime import date, timedelta

User = get_user_model()

class AdListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Vehicles')

        # Create multiple ads for testing filters and search
        self.ad1 = Ad.objects.create(
            title='MacBook Pro for sale',
            description='Like new MacBook Pro 2023.',
            user=self.user,
            is_active=True,
            category=self.category1,
            location='New York',
            price=1500.00,
            event_date=date.today()
        )
        self.ad2 = Ad.objects.create(
            title='iPhone 14',
            description='Used iPhone 14, in good condition.',
            user=self.user,
            is_active=True,
            category=self.category1,
            location='Los Angeles',
            price=700.00,
            event_date=date.today()
        )
        self.ad3 = Ad.objects.create(
            title='Honda Civic',
            description='2020 Honda Civic, low mileage.',
            user=self.user,
            is_active=True,
            category=self.category2,
            location='New York',
            price=22000.00,
            event_date=date.today() + timedelta(days=7)
        )
        self.ad4 = Ad.objects.create(
            title='Old Furniture',
            description='This is not active.',
            user=self.user,
            is_active=False,
            category=self.category2,
            location='Chicago',
            price=50.00,
            event_date=date.today()
        )
        
        self.client.login(username='testuser', password='password')

    def tearDown(self):
        Ad.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

    def test_search_by_keyword(self):
        response = self.client.get(reverse('ad_list'), {'q': 'MacBook'})
        self.assertEqual(len(response.context['ads']), 1)
        self.assertIn(self.ad1, response.context['ads'])

    def test_search_by_description_keyword(self):
        response = self.client.get(reverse('ad_list'), {'q': 'Honda'})
        self.assertEqual(len(response.context['ads']), 1)
        self.assertIn(self.ad3, response.context['ads'])

    def test_filter_by_category(self):
        response = self.client.get(reverse('ad_list'), {'category': self.category1.id})
        self.assertEqual(len(response.context['ads']), 2)
        self.assertIn(self.ad1, response.context['ads'])
        self.assertIn(self.ad2, response.context['ads'])
        self.assertNotIn(self.ad3, response.context['ads'])

    def test_filter_by_location(self):
        response = self.client.get(reverse('ad_list'), {'location': 'New York'})
        self.assertEqual(len(response.context['ads']), 2)
        self.assertIn(self.ad1, response.context['ads'])
        self.assertIn(self.ad3, response.context['ads'])
        self.assertNotIn(self.ad2, response.context['ads'])

    def test_filter_by_min_price(self):
        response = self.client.get(reverse('ad_list'), {'min_price': 1000})
        self.assertEqual(len(response.context['ads']), 2)
        self.assertIn(self.ad1, response.context['ads'])
        self.assertIn(self.ad3, response.context['ads'])
        self.assertNotIn(self.ad2, response.context['ads'])

    def test_filter_by_max_price(self):
        response = self.client.get(reverse('ad_list'), {'max_price': 1000})
        self.assertEqual(len(response.context['ads']), 1)
        self.assertIn(self.ad2, response.context['ads'])
        self.assertNotIn(self.ad1, response.context['ads'])
        self.assertNotIn(self.ad3, response.context['ads'])

    def test_combined_filters(self):
        response = self.client.get(reverse('ad_list'), {
            'q': 'MacBook',
            'category': self.category1.id,
            'min_price': 1000,
            'max_price': 2000,
            'location': 'New York'
        })
        self.assertEqual(len(response.context['ads']), 1)
        self.assertIn(self.ad1, response.context['ads'])

    def test_search_does_not_include_inactive_ads(self):
        response = self.client.get(reverse('ad_list'), {'q': 'Furniture'})
        self.assertEqual(len(response.context['ads']), 0)
        self.assertNotIn(self.ad4, response.context['ads'])
