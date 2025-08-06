from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import CustomUser, Category, Ad, AdImage, Message
from ordered_model.models import OrderedModel

"""
Get the custom user model to use in tests
"""
User = get_user_model()

class CustomUserModelTest(TestCase):
    def test_user_creation(self):
        """Test that a basic user can be created."""

        user = User.objects.create_user(username='testuser', password='password')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_str_representation(self):
        user = User.objects.create_user(username='testuser_str', password='password')
        self.assertEqual(str(user), 'testuser_str')

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """Test that a category can be created."""

        category = Category.objects.create(name='Electronics')
        self.assertEqual(category.name, 'Electronics')

    def test_str_representation(self):
        category = Category.objects.create(name='Vehicles')
        self.assertEqual(str(category), 'Vehicles')

class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ad_owner', password='password')
        self.category = Category.objects.create(name='General')

    def test_ad_creation(self):
        """Test that an ad can be created."""

        ad = Ad.objects.create(
            user=self.user,
            title='Test Ad Title',
            description='Test ad description.',
            category=self.category,
            location='Test Location',
            contact_info='test@example.com'
        )
        self.assertEqual(ad.title, 'Test Ad Title')
        self.assertEqual(ad.user, self.user)
        self.assertEqual(ad.category.name, 'General')

    def test_str_representation(self):
        ad = Ad.objects.create(
            user=self.user,
            title='Ad for Testing',
            description='Description',
            category=self.category,
            location='Test Location',
            contact_info='test@example.com'
        )
        self.assertEqual(str(ad), 'Ad for Testing')

class AdImageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='img_user', password='password')
        self.category = Category.objects.create(name='General')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad with Images',
            description='Testing images.',
            category=self.category,
            location='Test Location',
            contact_info='test@example.com'
        )

    def test_ad_image_creation(self):
        """Test that an image can be created and linked to an ad."""

        # Note: We're not uploading a real file here for simplicity
        image = AdImage.objects.create(ad=self.ad, image='dummy_image.jpg')
        self.assertEqual(image.ad, self.ad)
        self.assertEqual(image.image, 'dummy_image.jpg')
        self.assertIsInstance(image, OrderedModel)

    def test_str_representation(self):
        image = AdImage.objects.create(ad=self.ad, image='dummy.jpg')
        self.assertEqual(str(image), 'Image for Ad: Test Ad with Images')

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='password')
        self.recipient = User.objects.create_user(username='recipient', password='password')
        self.category = Category.objects.create(name='General')
        self.ad = Ad.objects.create(
            user=self.recipient,
            title='Ad for Message',
            description='Message test ad.',
            category=self.category,
            location='Test Location',
            contact_info='test@example.com'
        )

    def test_message_creation(self):
        """Test that a message can be created."""

        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            ad=self.ad,
            content='Hello, I am interested in this ad.'
        )
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.recipient, self.recipient)
        self.assertEqual(message.ad, self.ad)
        self.assertEqual(message.content, 'Hello, I am interested in this ad.')
        self.assertFalse(message.read)

    def test_str_representation(self):
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            ad=self.ad,
            content='Test message.'
        )
        self.assertEqual(str(message), 'Message from sender to recipient')
