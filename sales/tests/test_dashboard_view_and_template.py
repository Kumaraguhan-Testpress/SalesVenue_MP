from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from sales.models import Conversation, Message, Ad, Category

User = get_user_model()

class DashboardViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass1234",
            phone_number="1234567890",
            contact_info_visibility=True
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="pass1234"
        )
        self.category = Category.objects.create(name="Test Category")
        self.ad = Ad.objects.create(
            title="Test Ad",
            description="Description",
            price=100,
            user=self.user,
            category=self.category
        )
        self.conversation = Conversation.objects.create(
            ad=self.ad,
            owner=self.user,
            buyer=self.other_user
        )

    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_dashboard_renders_for_logged_in_user(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertContains(response, "User Dashboard")
        self.assertContains(response, self.user.username)

    def test_contact_info_visibility_enabled(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, '<span class="badge bg-success">Enabled</span>', html=True)

    def test_contact_info_visibility_disabled(self):
        self.user.contact_info_visibility = False
        self.user.save()
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, '<span class="badge bg-secondary">Disabled</span>', html=True)

    def test_conversations_listed(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, self.conversation.ad.title)

    def test_no_conversations_message(self):
        Conversation.objects.all().delete()
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "No conversations yet.")
