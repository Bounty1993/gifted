import datetime
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse

from src.accounts.forms import ProfileForm

User = get_user_model()


class SignUpViewTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='Tester',
            password='Tester123',
        )
        self.url = reverse('accounts:signup')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_post_data(self):
        data = {'username': 'Bartosz123', 'password1': 'Tester123',
                'password2': 'Tester123', 'bio': 'Hello'}
        response = self.client.post(self.url, data)
        user = self.user_model.objects.get(username='Bartosz123')
        self.assertEqual(user.profile.bio, 'Hello')


class ProfileFormTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='Tester',
            password='Tester123',
        )

    def test_profile_creation(self):
        date_birth = datetime.date(1993, 5, 23)
        data = {'date_birth': date_birth, 'bio': 'Hello World'}
        form = ProfileForm(
            data,
            instance=self.user.profile
        )
        self.assertTrue(form.is_valid())
        new_profile = form.save()
        self.assertEqual(new_profile.date_birth, date_birth)
        self.assertEqual(new_profile.bio, 'Hello World')

    def test_not_adult(self):
        today = datetime.datetime.now().date()
        form = ProfileForm(
            {'date_birth': today},
            instance=self.user
        )
        self.assertFalse(form.is_valid())
        adult_error = 'Podana data wskazuje, że nie jesteś dorosły.'
        self.assertEqual(form.errors['date_birth'], [adult_error])


class PasswordViewsTest(TestCase):
    def setUp(self):
        self.user = (
            User.objects.create_user(username='Testuser1', password='Tester123', email='test@gmail.com')
        )

    def test_change_view_status_code(self):
        url = reverse('accounts:change_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_view_post(self):
        self.client.force_login(self.user)
        url = reverse('accounts:change_password')
        data = {'new_password1': 'NoweHaslo123', 'new_password2': 'NoweHaslo123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        new_password = data['new_password1']
        self.assertTrue(self.user.check_password(new_password))

    def test_reset_password_status_code(self):
        url = reverse('accounts:reset_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_post(self):
        url = reverse('accounts:reset_password')
        data = {'email': self.user.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        reset_mail = mail.outbox[0]
        self.assertEqual(reset_mail.recipients()[0], self.user.email)

    def test_reset_key_password(self):
        url = reverse('accounts:reset_password')
        data = {'email': self.user.email}
        self.client.post(url, data)
        reset_mail = mail.outbox[0]
        key = re.search('/key/[\w-]+', reset_mail.body)
        key = key.group().split('/')[-1]
        uidb36, key = key.rsplit('-', 1)
        key_url = reverse(
            'accounts:account_reset_password_from_key',
            kwargs={'uidb36': uidb36, 'key': key}
        )
        response = self.client.post(key_url, follow=True)
        self.assertEqual(response.status_code, 200)
        expected = f'/accounts/password/reset/key/{self.user.id}-set-password/'
        self.assertEqual(response.redirect_chain[0][0], expected)
