from django.test import TestCase
from datetime import datetime
from django.contrib.auth import get_user_model
from src.rooms.models import Room

User = get_user_model()


class RoomTransactionModelTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='testuser', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        room1 = Room.objects.create(receiver='receiver1', gift='gift1', price=1000, description='test',
                 to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        room2 = Room.objects.create(receiver='receiver2', gift='gift2', price=900, description='test',
                 to_collect=900, visible=True, date_expires=datetime(2019, 6, 6))
        room3 = Room.objects.create(receiver='receiver3', gift='gift3', price=800, description='test',
                 to_collect=800, visible=True, date_expires=datetime(2019, 6, 6))

        room1.donate({'user': user1, 'amount': 500})
        room2.donate({'user': user1, 'amount': 300})
        room2.donate({'user': user2, 'amount': 200})
        room3.donate({'user': user1, 'amount': 200})
        room3.donate({'user': user2, 'amount': 200})
        room3.donate({'user': user3, 'amount': 200})

    def test_creation(self):
        room=Room.objects.get(receiver='receiver1')
        self.assertEqual(room.price, 1000)
        self.assertEqual(room.description, 'test')
        self.assertEqual(room.to_collect, 500)

    def test_str(self):
        room = Room.objects.get(receiver='receiver1')
        self.assertEqual(str(room), 'receiver1 - gift1')

    def test_most_patrons(self):
        most_patrons = Room.get_visible.most_patrons()
        expected = Room.objects.get(receiver='receiver3')
        self.assertEqual(most_patrons[0], expected)

    def test_most_popular(self):
        most_collected = Room.get_visible.most_popular()
        expected = Room.objects.get(receiver='receiver3')
        self.assertEqual(most_collected[0], expected)

    def test_most_to_collect(self):
        most_to_collect = Room.get_visible.most_to_collect()
        expected = Room.objects.get(receiver='receiver1')
        self.assertEqual(most_to_collect[0], expected)

    def test_buy(self):
        room = Room.objects.get(receiver='receiver1')
        user = User.objects.get(id=1)
        beginning = room.to_collect
        donate_amount = 200

        room.donate({'user': user, 'amount': donate_amount})
        rest = beginning - donate_amount
        self.assertEqual(room.to_collect, rest)

        room.donate({'user': user, 'amount': rest})
        self.assertFalse(room.is_active)
        self.assertEqual(room.to_collect, 0)

    def test_get_patrons(self):
        room3 = Room.objects.get(receiver='receiver2')
        patrons = room3.get_patrons()
        ordered_patrons = ['testuser', 'testuser2']
        self.assertEqual(list(patrons), ordered_patrons)
