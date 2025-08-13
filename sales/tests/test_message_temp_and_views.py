from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from sales.models import Ad, Conversation, Message, Category

class ViewsTestCase(TestCase):
    def setUp(self):
        CustomUser = get_user_model()
        self.user1 = CustomUser.objects.create_user(username='user1', email='user1@example.com', password='password')
        self.user2 = CustomUser.objects.create_user(username='user2', email='user2@example.com', password='password')
        self.user3 = CustomUser.objects.create_user(username='user3', email='user3@example.com', password='password')

        self.category = Category.objects.create(name='Electronics', description='Test category for ads')

        self.ad1 = Ad.objects.create(
            title='Test Ad 1', 
            user=self.user1, 
            category=self.category,
            description='A detailed description for Ad 1',
            location='Test Location A',
            contact_info='contact1@example.com'
        )
        self.ad2 = Ad.objects.create(
            title='Test Ad 2', 
            user=self.user2, 
            category=self.category,
            description='A detailed description for Ad 2',
            location='Test Location B',
            contact_info='contact2@example.com'
        )

        self.conversation = Conversation.objects.create(
            ad=self.ad1,
            owner=self.user1,
            buyer=self.user2
        )
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, this is a test message.'
        )

        self.client = Client()

    def test_start_conversation_new_conversation(self):
        self.client.login(username='user1', password='password')
        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('start_conversation', args=[self.ad1.pk]))
        self.assertEqual(Conversation.objects.count(), 1)
        new_conversation = Conversation.objects.last()
        self.assertRedirects(response, reverse('conversation_detail', args=[new_conversation.pk]))

    def test_start_conversation_existing_conversation(self):
        self.client.login(username='user2', password='password')
        response = self.client.get(reverse('start_conversation', args=[self.ad1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertRedirects(response, reverse('conversation_detail', args=[self.conversation.pk]))

    def test_start_conversation_unauthenticated(self):
        response = self.client.get(reverse('start_conversation', args=[self.ad1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_conversation_list_authenticated_user(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('conversation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversations/list.html')
        self.assertIn('conversations', response.context)
        self.assertEqual(len(response.context['conversations']), 1)

    def test_conversation_list_unauthenticated_user(self):
        response = self.client.get(reverse('conversation_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_conversation_detail_authorized_user(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('conversation_detail', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversations/detail.html')
        self.assertEqual(response.context['conversation'], self.conversation)
        self.assertIn('messages', response.context)
        self.assertIn('form', response.context)

    def test_conversation_detail_unauthorized_user(self):
        self.client.login(username='user3', password='password')
        response = self.client.get(reverse('conversation_detail', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 403)

    def test_conversation_detail_unauthenticated_user(self):
        response = self.client.get(reverse('conversation_detail', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 403)

    def test_conversation_detail_not_found(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('conversation_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_send_message_valid_data(self):
        self.client.login(username='user2', password='password')
        post_data = {'content': 'This is a new test message.'}
        response = self.client.post(reverse('send_message', args=[self.conversation.pk]), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['content'], 'This is a new test message.')
        self.assertEqual(self.conversation.messages.count(), 2)

    def test_send_message_invalid_data(self):
        self.client.login(username='user2', password='password')
        post_data = {'content': ''}
        response = self.client.post(reverse('send_message', args=[self.conversation.pk]), post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())
        self.assertEqual(self.conversation.messages.count(), 1)

    def test_send_message_unauthorized_user(self):
        self.client.login(username='user3', password='password')
        post_data = {'content': 'This should not work.'}
        response = self.client.post(reverse('send_message', args=[self.conversation.pk]), post_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.conversation.messages.count(), 1)

    def test_json_view_get_all_messages(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('conversation_messages_json', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['messages']), 1)

    def test_json_view_get_messages_after_timestamp(self):
        self.client.login(username='user2', password='password')
        old_message_time = self.message.sent_at
        new_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='A newer message.',
            sent_at=timezone.now() + timezone.timedelta(seconds=5)
        )
        response = self.client.get(
            reverse('conversation_messages_json', args=[self.conversation.pk]),
            {'after': old_message_time.isoformat()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['messages']), 1)
        self.assertEqual(response.json()['messages'][0]['content'], 'A newer message.')

    def test_json_view_unauthorized_user(self):
        self.client.login(username='user3', password='password')
        response = self.client.get(reverse('conversation_messages_json', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 403)

    def test_ad_conversation_list_unauthenticated_user(self):
        response = self.client.get(reverse('conversation_list_for_ad', args=[self.ad1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
