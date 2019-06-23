import factory, factory.django
from django.contrib.auth import get_user_model
from src.rooms.models import Room
from datetime import datetime

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'username_{n}')
    password = 'Tester123'


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    receiver = factory.Sequence(lambda n: f'receiver_{n}')
    creator = factory.SubFactory(UserFactory)
    gift = factory.Sequence(lambda n: 100 + n * 10)
    price = 10000
    description = factory.Faker('text')
    visible = True
    date_expires = datetime(2019, 9, 9)
    is_active = True
