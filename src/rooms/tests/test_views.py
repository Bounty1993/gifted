import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.views.generic import ListView

from src.rooms.models import Donation, Message, Room
from src.rooms.views import FilterSearchMixin

User = get_user_model()


class RoomRegistrationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tom',
            password='Test'
        )
        self.client.login(username='Tom', password='Test')

    def test_status_code(self):
        url = reverse('rooms:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_redirect_correct(self):
        data = {
            'receiver': 'my receiver',
            'gift': 'Samochód',
            'price': 1000,
            'description': 'Hello test',
            'visible': True,
            'date_expires': '29/10/2019',
        }
        url = reverse('rooms:register')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_room_creation(self):
        data = {
            'receiver': 'my receiver',
            'gift': 'Samochód',
            'price': 1000,
            'description': 'Hello test',
            'visible': True,
            'date_expires': '29/10/2019',
        }
        url = reverse('rooms:register')
        self.client.post(url, data)
        self.assertTrue(Room.objects.exists())
        room = Room.objects.get(receiver='my receiver')
        self.assertEqual(room.to_collect, room.price)

    def test_incorrect_data(self):
        data = {
            'receiver': 'my receiver',
            'gift': 'Samochód',
            'price': 1000,
            'description': 'Hello test',
        }
        url = reverse('rooms:register')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Room.objects.exists())


class RoomListViewTest(TestCase):
    def setUp(self):
        url = reverse('rooms:list')
        self.response = self.client.get(url)

    def test_response_code(self):
        self.assertEqual(self.response.status_code, 200)


class FilterSearchMixinTest(TestCase):
    def setUp(self):
        pass

    class ExampleView(FilterSearchMixin, ListView):
        pass


class RoomDetailViewTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']

    def setUp(self):
        user1 = User.objects.get(username='testuser')
        self.room1 = Room.objects.get(gift='gift1')
        self.room1.donate({'user': user1, 'amount': 500})

    def test_status_code_correct(self):
        url = reverse('rooms:detail', kwargs={'pk': self.room1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_status_code_incorrect(self):
        url = reverse('rooms:detail', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DonationListViewTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']

    def setUp(self):
        self.user1 = User.objects.get(username='testuser')
        self.user2 = User.objects.get(username='testuser2')
        self.room1 = Room.objects.get(gift='gift1')
        self.room1.donate({'user': self.user1, 'amount': 500})
        self.room1.donate({'user': self.user2, 'amount': 100})

    def test_status_code(self):
        url = reverse('rooms:donation', kwargs={'pk': self.room1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_chart_data(self):
        Donation.objects.create(user=self.user1, room=self.room1, amount=200)
        Donation.objects.filter(amount=200).update(
            date=datetime(2019, 6, 6).date()
        )
        url = reverse('rooms:donation_chart', kwargs={'pk': self.room1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        expected = [200, 600]
        self.assertEqual(content['series'][0]['data'], list(expected))
        today = datetime.now().date()
        expected = ['2019-06-06', today.strftime('%Y-%m-%d')]
        self.assertEqual(content['xAxis']['categories'], expected)


class DonateViewTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']

    def setUp(self):
        self.user1 = User.objects.get(username='testuser')
        self.user2 = User.objects.get(username='testuser2')
        self.user3 = User.objects.get(username='testuser3')
        self.room1 = Room.objects.get(gift='gift1')
        self.room2 = Room.objects.get(gift='gift3')
        self.room2.guests.add(self.user2)
        self.user = User.objects.create_user(
            username='Tom',
            password='Test'
        )
        self.client.login(username='Tom', password='Test')

    def test_status_code(self):
        url = reverse('rooms:detail', kwargs={'pk': self.room1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_forbid_to_see_user(self):
        self.client.login(username='testuser3', password='12345')
        url = reverse('rooms:detail', kwargs={'pk': self.room2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


def make_ajax(client, url, data=None):
    response = client.post(
        url,
        json.dumps(data),
        'json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    return response


class ObserverViewTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']

    def setUp(self):
        self.user1 = User.objects.get(username='testuser')
        self.user2 = User.objects.get(username='testuser2')
        self.room = Room.objects.get(gift='gift1')
        self.client.force_login(self.user1)

    def test_status_code(self):
        url = reverse('rooms:observers', kwargs={'pk': self.room.id})
        response = make_ajax(self.client, url)
        self.assertEqual(response.status_code, 200)

    def test_observer_added(self):
        url = reverse('rooms:observers', kwargs={'pk': self.room.id})
        response = make_ajax(self.client, url)
        self.assertTrue(self.room.observers.exists())
        self.assertEqual(self.room.observers.first().id, self.user1.id)
        response_data = json.loads(response.content)
        expected = {'is_valid': 'true'}
        self.assertEqual(response_data, expected)


class MakeMessageViewTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']

    def setUp(self):
        self.user1 = User.objects.get(username='testuser')
        self.user2 = User.objects.get(username='testuser2')
        self.room = Room.objects.get(gift='gift1')
        self.client.force_login(self.user1)

        self.data = {
            'receiver': self.user2.id,
            'subject': 'Tytuł',
            'content': 'Treść',
        }

    def test_status_code(self):
        response = make_ajax(self.client, reverse('rooms:message'), self.data)
        self.assertEqual(response.status_code, 200)

    def test_message_creation(self):
        make_ajax(self.client, reverse('rooms:message'), self.data)
        self.assertTrue(Message.objects.exists())

    def test_message_data(self):
        make_ajax(self.client, reverse('rooms:message'), self.data)
        message = Message.objects.first()
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.subject, 'Tytuł')
        self.assertEqual(message.content, 'Treść')

    def test_message_return(self):
        response = make_ajax(self.client, reverse('rooms:message'), self.data)
        response_data = json.loads(response.content)
        expected = {'is_valid': 'true'}
        self.assertEqual(response_data, expected)


class DeleteMessageViewTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser', password='12345'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', password='12345'
        )
        self.room = Room.objects.create(
            receiver='receiver1', creator=self.user1,
            gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        self.message = Message.objects.create(
            receiver=self.user1, sender=self.user2,
            subject='Tytuł', content='Treść'
        )
        self.client.login(username='testuser', password='12345')
        self.data = {'id': self.message.id}

    def test_status_code(self):
        response = make_ajax(
            self.client, reverse('rooms:message_delete'), self.data
        )
        self.assertEqual(response.status_code, 200)

    def test_message_delete(self):
        response = make_ajax(
            self.client, reverse('rooms:message_delete'), self.data
        )
        self.assertFalse(Message.objects.exists())
        response_data = json.loads(response.content)
        expected = {'is_valid': 'true'}
        self.assertEqual(response_data, expected)
