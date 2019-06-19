import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Q, Sum
from django.test import TestCase
from django.urls import reverse

from src.rooms.models import Room

from ..models import Post, Thread

User = get_user_model()


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345')
        room = Room.objects.create(
            receiver='receiver1', gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6)
        )
        self.url = reverse('forum:create', kwargs={'pk': room.pk})
        self.response = self.client.get(self.url)
        self.client.login(username='testuser', password='12345')

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


class AllPostListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345')
        self.room1 = Room.objects.create(
            receiver='receiver1', gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6)
        )
        self.post1 = Post.objects.create(room=self.room1, author=self.user1, subject='Post1', content='Test1')
        self.post2 = Post.objects.create(room=self.room1, author=self.user1, subject='Post2', content='Test2')
        self.thread1 = Thread.objects.create(
            author=self.user1, post=self.post1,
            subject='Thread1', content='Test1'
        )
        self.client.login(username='testuser', password='12345')

    def test_no_search_view(self):
        url = reverse('forum:all')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        queryset = response.context['posts']
        self.assertEqual(queryset.count(), 2)
        self.assertTrue(queryset.first().score)
        self.assertEqual(response.context['num_posts'], Post.objects.count())

    def test_search_view(self):
        url = reverse('forum:all')
        response = self.client.get(url, {'search': self.thread1.subject})
        self.assertEqual(response.status_code, 200)
        queryset = response.context['posts']
        self.assertEqual(queryset.count(), 1)


def make_ajax(client, url, data=None):
    response = client.post(
        url,
        json.dumps(data),
        'json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    return response


class AjaxViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.room1 = Room.objects.create(receiver='receiver1', gift='gift1', price=1000, description='test',
                                    to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        self.post1 = Post.objects.create(room=self.room1, author=self.user1, subject='Post1', content='Test1')
        self.post2 = Post.objects.create(room=self.room1, author=self.user1, subject='Post2', content='Test2')
        self.thread1 = Thread.objects.create(
            author=self.user1, post=self.post1,
            subject='Thread1', content='Test1'
        )
        self.thread2 = Thread.objects.create(
            author=self.user1, post=self.post1,
            subject='Thread1', content='Test1', parent=self.thread1
        )
        self.client.login(username='testuser', password='12345')

    def test_add_like_thread_view(self):
        initial_likes = self.thread1.get_likes()
        url = reverse('forum:add_like')
        data = {'id': '1', 'is_thread': 'true'}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected_likes = initial_likes + 1
        actual = Thread.objects.get(id=1).get_likes()
        self.assertEqual(actual, expected_likes)
        expected_response = {'success': 'true', 'num_likes': actual}
        self.assertEqual(json.loads(response.content), expected_response)

    def test_add_like_post_view(self):
        initial_likes = self.post1.get_likes()
        url = reverse('forum:add_like')
        data = {'id': '1'}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected_likes = initial_likes + 1
        actual = Post.objects.get(id=1).get_likes()
        self.assertEqual(actual, expected_likes)
        expected_response = {'success': 'true', 'num_likes': actual}
        self.assertEqual(json.loads(response.content), expected_response)

    def test_add_dislike_thread_view(self):
        initial_likes = self.thread1.get_likes()
        url = reverse('forum:add_dislike')
        data = {'id': '1', 'is_thread': 'true'}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected_likes = initial_likes - 1
        actual = Thread.objects.get(id=1).get_likes()
        self.assertEqual(actual, expected_likes)
        expected_response = {'success': 'true', 'num_likes': actual}
        self.assertEqual(json.loads(response.content), expected_response)

    def test_add_dislike_post_view(self):
        initial_likes = self.post1.opinions.aggregate(Sum('likes')).get('likes_sum', 0)
        url = reverse('forum:add_dislike')
        data = {'id': '1'}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected_likes = initial_likes - 1
        actual = Post.objects.get(id=1).get_likes()
        self.assertEqual(actual, expected_likes)
        expected_response = {'success': 'true', 'num_likes': actual}
        self.assertEqual(json.loads(response.content), expected_response)

    def test_get_threads_post_view(self):
        post_id = self.post1.id
        url = reverse('forum:thread_list', kwargs={'pk': self.room1.id})
        data = {'post_id': post_id}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected = {
            'is_valid': 'true',
            'threads': Thread.objects.get_main(post_id=post_id)
        }
        actual = json.loads(response.content)
        self.assertEqual(actual['is_valid'], 'true')
        # self.assertEqual(actual, expected)

    def test_get_threads_thread_view(self):
        thread_id = self.thread1.id
        url = reverse('forum:thread_list', kwargs={'pk': self.room1.id})
        data = {'thread_id': thread_id}
        response = make_ajax(self.client, url, data)
        self.assertEqual(response.status_code, 200)
        expected = {
            'is_valid': 'true',
            'threads': Thread.objects.get_secondary(thread_id=thread_id)
        }
        actual = json.loads(response.content)
        self.assertEqual(actual['is_valid'], 'true')
        # self.assertEqual(actual, expected)

    def test_post_delete_view(self):
        post = self.post1
        room_id = post.room.id
        url = reverse('forum:delete', kwargs={'pk': room_id, 'post_pk': post.id})
        response = self.client.delete(
            url, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_delete_incorrect_user_view(self):
        self.client.login(username='testuser2', password='12345')
        post = self.post1
        room_id = post.room.id
        url = reverse('forum:delete', kwargs={'pk': room_id, 'post_pk': post.id})
        response = self.client.delete(
            url, HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 401)

    def test_update_view(self):
        post = self.post1
        url = reverse('forum:edit', kwargs={'pk': post.room.id, 'post_pk': post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_incorect_view(self):
        post = self.post1
        url = reverse('forum:edit', kwargs={'pk': post.room.id, 'post_pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_post_view(self):
        post = self.post1
        url = reverse('forum:edit', kwargs={'pk': post.room.id, 'post_pk': post.id})
        data = {
            'subject': 'New subject',
            'content': 'New Content'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
