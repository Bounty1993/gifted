import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict

from .forms import DonateForm
from .models import Room


class DonateConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        form = DonateForm(data)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            comment = form.cleaned_data.get('comment')
            data = {
                'user': self.scope['user'],
                'amount': amount,
                'comment': comment
            }
            room_id = int(self.room_id)
            room = Room.objects.get(id=room_id).donate(data)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'to_collect': str(room.to_collect),
                    'collected': str(room.collected()),
                    'percent_got': str(room.percent_got),
                }
            )
            return self.send(text_data=json.dumps({
                'is_valid': 'true'
            }))
        print(form.errors)
        return self.send(text_data=json.dumps({
            'is_valid': 'false',
            'errors': form.errors
        }))

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'to_collect': event['to_collect'],
            'collected': event['collected'],
            'percent_got': event['percent_got'],
        }))
