import json

from channels.generic.websocket import WebsocketConsumer

from .forms import DonateForm


class DonateConsumer(WebsocketConsumer):
    def connect(self):
        print('Hello')
        self.accept()

    def disconnect(self):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        form = DonateForm(data)
        if form.is_valid():
            return self.send(text_data=json.dumps({
                'message': 'correct'
            }))
        print(form.errors)
        return self.send(text_data=json.dumps({
            'message': 'wrong'
        }))
