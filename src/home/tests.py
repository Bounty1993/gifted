import json
from unittest import skip

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .forms import ContactForm

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

    def test_contact_view_post_with_email(self):
        mail.outbox = []
        url = reverse('home:contact')
        data = {'subject': 'Tytuł', 'message': 'Treść', 'email': 'bartosz@wp.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(*mail.outbox[0].to, data['email'])

    @skip
    def test_contact_view_post_with_user(self):
        url = reverse('home:contact')
        data = {'subject': 'Tytuł', 'message': 'Treść'}
        self.client.login(username='Bartosz', password='12345')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(*mail.outbox[0].to, self.user.email)

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

    def test_validate_email_view(self):
        url = reverse('home:validate_email', kwargs={'email': self.user1.email})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        expected = {'is_taken': 'true'}
        self.assertEqual(content, expected)
        url = reverse('home:validate_email', kwargs={'email': 'Losowy'})
        response = self.client.get(url)
        content = json.loads(response.content)
        expected = {'is_taken': 'false'}
        self.assertEqual(content, expected)


class ContactFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='12345', email='TEST')

    def test_valid_form_no_email(self):
        data = {'user': self.user1.id, 'subject': 'Tytuł', 'message': 'Treść'}
        form = ContactForm(data)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_email(self):
        data = {'subject': 'Tytuł', 'message': 'Treść', 'email':'bartosz@wp.com'}
        form = ContactForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_with_email(self):
        data = {'subject': 'Tytuł', 'message': 'Treść'}
        form = ContactForm(data)
        self.assertFalse(form.is_valid())
