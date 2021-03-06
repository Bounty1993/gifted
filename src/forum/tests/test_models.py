from datetime import datetime
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase

from src.rooms.models import Room

from ..models import Opinion, Post

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        room = Room.objects.create(
            receiver='receiver1', gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6)
        )
        self.post = Post.objects.create(
            room=room,
            author=self.user,
            subject='Test',
            content='Test content',
        )
        self.post2 = Post.objects.create(
            room=room,
            author=self.user,
            subject='Nowy post',
            content='Drugi post'
        )

    def test_post_creation(self):
        self.assertTrue(Post.objects.exists())

    def test_post_data(self):
        self.assertEqual(self.post.subject, 'Test')
        self.assertEqual(self.post.content, 'Test content')

    def test_get_likes_empty(self):
        self.assertEqual(self.post.get_likes(), 0)

    def test_date_creation(self):
        self.assertTrue(self.post.date)

    def test_search(self):
        author_name = self.user.username
        found = Post.visible.search(author_name)
        self.assertTrue(found.exists())
        found = Post.visible.search('nowy post')
        self.assertEqual(found.count(), 1)

    def test_summarise(self):
        pass

    def test_add_like(self):
        self.post.add_like(self.user)
        self.assertEqual(self.post.opinions.first().likes, 1)

    def test_add_dislike(self):
        self.post.add_dislike(self.user)
        self.assertEqual(self.post.opinions.first().likes, -1)

    def test_get_likes(self):
        self.post.add_like(self.user)
        self.assertEqual(self.post.get_likes(), 1)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        room = Room.objects.create(
            receiver='receiver1', gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6)
        )
        self.post = Post.objects.create(
            room=room,
            author=self.user,
            subject='Test',
            content='Test content',
        )

    def test_create(self):
        self.post.add_like(self.user)
        self.assertEqual(Opinion.objects.count(), 1)
