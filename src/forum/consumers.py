from channels.generic.websocket import WebsocketConsumer
import json
from django.forms.models import model_to_dict
from .forms import ThreadCreateForm
from .models import Thread


class PostConsumer(WebsocketConsumer):
    def connect(self):
        print('I am connected')
        self.accept()

    def disconnect(self):
        self.close()

    def receive(self, text_data):
        json_data = json.loads(text_data)
        author = self.scope['user']
        parent_thread = json_data.get('parent', None)
        if parent_thread:
            parent_thread = int(parent_thread)
            json_data['post_id'] = Thread.objects.get(id=parent_thread).post_id
        print(json_data)
        thread_data = {
            'author': author.id,
            'post': int(json_data['post_id']),
            'subject': json_data['subject'],
            'content': json_data['content'],
            'parent': parent_thread
        }
        form = ThreadCreateForm(thread_data)
        if form.is_valid():
            thread = form.save()
            print(thread)
            thread_dict = model_to_dict(thread)
            thread_dict['date'] = thread.date.strftime('%d.%m.%y %H:%M')
            thread_dict['author'] = author.username
            thread_dict['thread_parent'] = parent_thread
            print(thread_dict)
            self.send(text_data=json.dumps(
                thread_dict
            ))
        self.send(text_data=json.dumps(
            form.errors
        ))
