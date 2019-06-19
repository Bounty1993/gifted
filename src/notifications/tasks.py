from datetime import datetime

from django.core import mail
from django.core.mail import EmailMessage

from src.rooms.models import Donation, Room


def send_email(data):
    message = EmailMessage(data['subject'], data['message'], to=data['to'])
    return message.send()


def send_mass_email(email_message_list):
    connection = mail.get_connection()
    messages = email_message_list
    return connection.send_messages(messages)


# will be shared task
def close_rooms():
    today = datetime.now().date()
    outdated_rooms = Room.objects.filter(expires__lt=today)
    for room in outdated_rooms:
        notify_creator(room)
        notify_interested(room)
        room.is_active = False
        room.save()


# will be shared tasks
def room_collected(id):
    room = Room.objects.get(id=id)
    notify_creator(room)
    notify_interested(room)
    room.is_active = False
    room.save()


def notify_creator(room):
    resume = Donation.objects.filter(room_id=room.id).resume()
    message = {
        'subject': 'Tytuł',
        'message': resume,
        'to': ['bartosz@wp.com',]
    }
    return send_email(message)


def notify_interested(room):
    subject = f'Została zakończona zbiórka {room.gift}'
    with open('./interested_email.txt') as body:
        body = body.replace('<osiąginięto>', room.collected)
    interested = room.get_interested()
    messages = []
    for user in interested:
        messages.append(EmailMessage(
            'Zbiórka została zakończona',
            body,
            to=[user.email],
        ))
    send_mass_email(messages)
