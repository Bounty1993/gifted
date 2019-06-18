import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeViewsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Bartosz', password='12345', email='TEST')

    def test_home_view(self):
        url = reverse('home:main')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_view_status_code(self):
        url = reverse('home:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_email_view(self):
        url = reverse('home:get_email', kwargs={'pk': self.user1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        expected = {'pk': str(self.user1.id), 'email': self.user1.email}
        self.assertEqual(content, expected)
        url = reverse('home:get_email', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)