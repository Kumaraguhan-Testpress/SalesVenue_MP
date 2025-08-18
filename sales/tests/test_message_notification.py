from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from sales.models import Ad, Category, Conversation, Message

User = get_user_model()


class ConversationListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.buyer = User.objects.create_user(username="buyer", password="pass123")

        self.category = Category.objects.create(name="Test Category")
        self.ad = Ad.objects.create(
            title="Test Ad",
            category=self.category,
            user=self.owner,
            price=100,
            description="Test ad description",
        )

        self.conversation = Conversation.objects.create(
            ad=self.ad,
            owner=self.owner,
            buyer=self.buyer,
            created_at=timezone.now(),
        )

    def test_conversation_list_view_displays_conversation(self):
        self.client.login(username="owner", password="pass123")
        response = self.client.get(reverse("conversation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Ad")
        self.assertContains(response, "buyer")

    def test_unread_message_badge_displayed(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content="Hello!",
            read=False,
        )
        self.client.login(username="owner", password="pass123")
        response = self.client.get(reverse("conversation_list"))

    def test_no_unread_message_badge(self):
        Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content="Hello!",
            read=True,
        )
        self.client.login(username="owner", password="pass123")
        response = self.client.get(reverse("conversation_list"))
        self.assertNotContains(response, "(Have unread)")

    def test_no_conversations_message(self):
        Conversation.objects.all().delete()
        self.client.login(username="owner", password="pass123")
        response = self.client.get(reverse("conversation_list"))
        self.assertContains(response, "No conversations yet.")
