from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from datetime import datetime
from django.contrib.auth import get_user_model
from src.rooms.models import Room

User = get_user_model()


class RoomRegistrationViewTest(TestCase):

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
            'date_expires': '29/05/2019',
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
            'date_expires': '29/05/2019',
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


class RoomDetailViewTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='testuser', password='12345')
        room1 = Room.objects.create(receiver='receiver1', gift='gift1', price=1000, description='test',
                                    to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        room1.donate({'user': user1, 'amount': 500})

    def test_status_code_correct(self):
        url = reverse('rooms:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_status_code_incorrect(self):
        url = reverse('rooms:detail', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DonateViewTest(TestCase):
    pass

