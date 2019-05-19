from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from ..models import Post
from src.rooms.models import Room
from django.contrib.auth import get_user_model

User = get_user_model()


class PostCreateViewTest(TestCase):
    def setUp(self):
        room = Room.objects.create(
            receiver='receiver1', gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6)
        )
        self.url = reverse('forum:create', kwargs={'pk': room.pk})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_redirect_correct(self):
        data = {
            'subject': 'Test',
            'content': 'Test content',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_post_creation(self):
        data = {
            'subject': 'Test',
            'content': 'Test content',
        }
        self.client.post(self.url, data)
        self.assertTrue(Post.objects.exists())

    def test_status_code_incorrect(self):
        data = {
            'content': 'Test content',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
