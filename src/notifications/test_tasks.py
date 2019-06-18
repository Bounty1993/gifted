from django.test import TestCase
from django.core import mail
from src.rooms.models import Room
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from datetime import datetime
from src.notifications.tasks import (
    send_email,
    send_mass_email,
    notify_creator,
)

User = get_user_model()


class TasksTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345', email='testuser@test.pl')
        self.user2 = User.objects.create_user(username='testuser2', password='12345', email='testuser2@test.pl')

        self.room1 = Room.objects.create(
            receiver='receiver1', creator=self.user1, gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        self.room1.donate({'user': self.user1, 'amount': 500})

    def test_send_mail(self):
        mail.outbox = []
        message = {'subject':'Tytuł', 'message': 'Co tam', 'to': ['bartosz@wp.com', ]}
        send_email(message)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_mass_email(self):
        mail.outbox = []
        message = EmailMessage('Tytuł', 'Co tam', to=['bartosz@wp.com', ])
        messages = [message] * 5
        send_mass_email(messages)
        self.assertEqual(len(mail.outbox), 5)

    def test_notify_creator(self):
        mail.outbox = []
        notify_creator(self.room1)
        self.assertEqual(len(mail.outbox), 1)

    """
    def test_notify_interested(self):
        notify_interested(self.room1)
    """
