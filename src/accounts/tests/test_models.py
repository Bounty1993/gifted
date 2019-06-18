from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Profile
from django.core.mail import outbox

User = get_user_model()


class TestProfileModel(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Bartosz', password='12345', email='TEST')

    def test_profile_creation(self):
        profile = Profile.objects.filter(user_id=self.user1.id)
        self.assertTrue(profile.exists())

    def test_mail_sent(self):
        self.user1 = User.objects.create_user(username='Bartosz1', password='12345', email='TEST')
        self.assertEqual(len(outbox), 1)
        username = self.user1.username
        self.assertEqual(outbox[0].subject, f'Witaj {username} Założyłeś właśnie konto w Gifted')

    def test_full_name(self):
        profile = Profile.objects.filter(user_id=self.user1.id).first()
        self.assertEqual(profile.full_name, self.user1.username)