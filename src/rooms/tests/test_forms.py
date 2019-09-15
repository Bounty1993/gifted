from datetime import date

from django.test import TestCase
from django.forms.models import model_to_dict

from ..models import Room, Donation
from ..forms import DonateForm, RoomRegisterForm, RoomUpdateForm


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

    def test_room_update_name(self):
        room = Room.objects.get(gift='gift1')
        data = model_to_dict(room)
        data['gift'] = 'Surfing'
        form = RoomUpdateForm(data, instance=room)
        self.assertTrue(form.is_valid())
