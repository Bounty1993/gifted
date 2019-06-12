from channels.generic.websocket import WebsocketConsumer
import json
from django.forms.models import model_to_dict
from .forms import ThreadCreateForm


class PostConsumer(WebsocketConsumer):
    def connect(self):
        print('I am connected')
        self.accept()

    def disconnect(self):
        self.close()

    def receive(self, text_data):
        json_data = json.loads(text_data)
        author = self.scope['user']
        try:
            parent_thread = json_data['parent']
        except KeyError:
            parent_thread = None
        thread_data = {
            'author': author.id,
            'post': int(json_data['parentId']),
            'subject': json_data['subject'],
            'content': json_data['content'],
            'parent': parent_thread
        }
        form = ThreadCreateForm(thread_data)
        if form.is_valid():
            thread = form.save(commit=False)
            thread_dict = model_to_dict(thread)
            thread_dict['author'] = author.username
            self.send(text_data=json.dumps(
                thread_dict
            ))
        self.send(text_data=json.dumps(
            form.errors
        ))
