from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.test import TestCase

from src.rooms.models import Donation, Room

User = get_user_model()


class RoomTransactionModelTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='testuser', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        room1 = Room.objects.create(
            receiver='receiver1', creator=user1, gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))
        room2 = Room.objects.create(
            receiver='receiver2', creator=user1, gift='gift2', price=900, description='test',
            to_collect=900, visible=True, date_expires=datetime(2019, 6, 6))
        room3 = Room.objects.create(
            receiver='receiver3', creator=user1, gift='gift3', price=800, description='test',
            to_collect=800, visible=True, date_expires=datetime(2019, 6, 6))

        room1.donate({'user': user1, 'amount': 500})
        room2.donate({'user': user1, 'amount': 300})
        room2.donate({'user': user2, 'amount': 200})
        room3.donate({'user': user1, 'amount': 200})
        room3.donate({'user': user2, 'amount': 200})
        room3.donate({'user': user3, 'amount': 200})

        self.room = Room.objects.get(receiver='receiver1')
        self.room2 = Room.objects.get(pk=room2.id)

        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.user3 = User.objects.get(id=3)

    def test_creation(self):
        room = Room.objects.get(receiver='receiver1')
        self.assertEqual(room.price, 1000)
        self.assertEqual(room.description, 'test')
        self.assertEqual(room.to_collect, 500)

    def test_str(self):
        room = Room.objects.get(receiver='receiver1')
        self.assertEqual(str(room), 'receiver1 - gift1')

    """
    def test_save(self):
        before_score = self.room.score
        self.room.donate({'user': self.user1, 'amount': 5})
        after_score = self.room.score
        print(self.room.score)
        self.assertTrue(after_score > before_score)
    """

    def test_percent_left(self):
        all_donations = (Donation.objects
            .filter(room=self.room)
            .aggregate(Sum('amount'))['amount__sum'])
        expected = (all_donations / self.room.price) * 100
        self.assertEqual(self.room.percent_left, expected)

    def test_percent_got(self):
        expected = 100 - self.room.percent_left
        self.assertEqual(self.room.percent_got, expected)

    def test_patrons_count(self):
        expected = (Donation.objects
                    .filter(room=self.room2)
                    .aggregate(Count('user'))['user__count'])
        self.assertEqual(self.room2.num_patrons, expected)

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

    def test_add_observer(self):
        num_observers = self.room.observers.count()
        self.room.add_observer(1)
        num_observers += 1
        self.assertEqual(self.room.observers.count(), num_observers)
        user = User.objects.get(id=1)
        self.assertTrue(user in self.room.observers.all())

    def test_donate(self):
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

    def test_get_visible(self):
        room3 = Room.objects.create(
            receiver='receiver3', creator=self.user1, gift='gift3', price=800, description='test',
            to_collect=800, visible=False, date_expires=datetime(2019, 6, 6))
        query = Room.objects.get_visible(self.user3)
        self.assertFalse(room3 in query)
        room3.guests.add(self.user2)
        query = Room.objects.get_visible(self.user2)
        self.assertTrue(room3 in query)

    def test_get_patrons(self):
        room3 = Room.objects.get(receiver='receiver2')
        patrons = room3.get_patrons()
        ordered_patrons = ['testuser', 'testuser2']
        self.assertEqual(list(patrons), ordered_patrons)

    def test_remove_guest(self):
        user = User.objects.first()
        self.room.guests.add(user)
        self.assertTrue(self.room.guests.filter(id=user.id))
        self.room.guest_remove(user.username)
        self.assertFalse(self.room.guests.filter(id=user.id))

    def test_get_guests_dict(self):
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
        self.room.guests.add(user1, user2)
        expected = [user1.username, user2.username]
        guest_list = self.room.get_guests_dict()

        self.assertEqual(guest_list, expected)


class DonationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='12345')
        self.room1 = Room.objects.create(
            receiver='receiver1', creator=self.user1, gift='gift1', price=1000, description='test',
            to_collect=1000, visible=True, date_expires=datetime(2019, 6, 6))

        self.room1.donate({'user': self.user1, 'amount': 500})

    def test_donation_exists(self):
        self.assertTrue(Donation.objects.exists())

    def test_donation_fields(self):
        donation = Donation.objects.first()
        self.assertEqual(donation.user, self.user1)
        self.assertEqual(donation.amount, 500)
        self.assertEqual(donation.room, self.room1)
        self.assertEqual(donation.date, datetime.now().date())

    def test_str(self):
        donation = Donation.objects.first()
        expected = f'{donation.room} - {donation.amount}'
        self.assertEqual(str(donation), expected)
