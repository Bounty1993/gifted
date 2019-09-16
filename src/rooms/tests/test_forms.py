from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.forms.models import model_to_dict

from ..models import Room, Donation
from ..forms import (
    DonateForm, RoomRegisterForm, RoomUpdateForm, MessageForm
)

User = get_user_model()


class RoomFormsTest(TestCase):
    fixtures = ['src/rooms/tests/fixtures.json']
    def setUp(self):
        self.room_data = {
            'receiver': 'my receiver',
            'gift': 'Samochód',
            'price': 1000,
            'description': 'Hello test',
            'date_expires': date(2019, 12, 31)
        }

    def test_room_creation(self):
        form = RoomRegisterForm(self.room_data)
        self.assertTrue(form.is_valid())

    def test_room_creation_incorrect(self):
        self.room_data['date_expires'] = date(2021, 10, 10)
        form = RoomRegisterForm(self.room_data)
        self.assertFalse(form.is_valid())
        errors = form.errors
        expected = 'Data wygaśnięcia nie może byc późniejsza niż 183 dni'
        self.assertEqual(errors['date_expires'][0], expected)

    def test_room_update_name(self):
        room = Room.objects.get(gift='gift1')
        data = model_to_dict(room)
        data['gift'] = 'Surfing'
        form = RoomUpdateForm(data, instance=room)
        self.assertTrue(form.is_valid())
        new_room = form.save()
        self.assertEqual(new_room.gift, 'Surfing')

    def test_room_update_incorrect_future_date(self):
        room = Room.objects.get(gift='gift1')
        data = model_to_dict(room)
        data['date_expires'] = date(2021, 10, 10)
        form = RoomUpdateForm(data, instance=room)
        self.assertFalse(form.is_valid())
        errors = form.errors
        expected = 'Zbiórka nie może trwać dłużej niż 183 dni od utworzenia'
        self.assertEqual(errors['date_expires'][0], expected)

    def test_room_update_incorrect_past_date(self):
        room = Room.objects.get(gift='gift1')
        data = model_to_dict(room)
        data['date_expires'] = date(2018, 10, 10)
        form = RoomUpdateForm(data, instance=room)
        self.assertFalse(form.is_valid())
        errors = form.errors
        expected = 'Data wygraśnięcia musi być w przyszłości'
        self.assertEqual(errors['date_expires'][0], expected)

    def test_message_form(self):
        receiver = User.objects.get(id=1)
        sender = User.objects.get(id=2)
        message_data = {
            'receiver': receiver.id,
            'sender': sender.id,
            'subject': 'test subject',
            'content': 'test content',
        }
        form = MessageForm(message_data)
        self.assertTrue(form.is_valid())
        message = form.save()
        self.assertEqual(message.sender, sender)

    def test_message_incorrect(self):
        sender = User.objects.get(id=2)
        message_data = {
            'receiver': sender.id,
            'sender': sender.id,
            'subject': 'test subject',
            'content': 'test content',
        }
        form = MessageForm(message_data)
        self.assertFalse(form.is_valid())
        errors = form.non_field_errors()
        expected = 'Odbiorca i nadawca nie mogą być tacy sami'
        self.assertEqual(errors[0], expected)

    def test_donation_form(self):
        donate_data = {'amount': '1000.00', 'comment': 'test'}
        form = DonateForm(donate_data)
        self.assertTrue(form.is_valid())
        donate_data['amount'] = '0.1'
        form = DonateForm(donate_data)
        self.assertFalse(form.is_valid())
        errors = form.errors
        expected = f'Wprowadzona kwota: 0.10. Minimalna kwota to 1 PLN'
        self.assertEqual(errors['amount'][0], expected)
