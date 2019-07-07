import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict

from .forms import ThreadCreateForm
from .models import Thread


class ThreadConsumer(WebsocketConsumer):
    """
    Consumer is responsible for creating a new threads. It gets
    text_data ('subject', 'content' and 'post_id'). Optionally there
    can be 'parent' ('thread_id') in text_data.
    Then new thread will be a comment to a parent,
    otherwise new thread will be direct comment to the parent post.
    """
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.forum_group_name = f'forum_{self.room_id}'

        print(f'connected to {self.forum_group_name}')
        async_to_sync(self.channel_layer.group_add)(
            self.forum_group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self):
        self.close()

    def receive(self, text_data):
        json_data = json.loads(text_data)
        author = self.scope['user']
        parent_thread = json_data.get('parent', None)
        # check if new thread should be
        # direct comment to the post or comment to the thread
        if parent_thread:
            parent_thread = int(parent_thread)
            json_data['post_id'] = Thread.objects.get(id=parent_thread).post_id
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

            thread_dict = model_to_dict(thread)
            thread_dict['date'] = thread.date.strftime('%d.%m.%y %H:%M')
            thread_dict['author'] = author.username
            thread_dict['thread_parent'] = parent_thread

            return async_to_sync(self.channel_layer.group_send)(
                self.forum_group_name,
                {
                    'type': 'chat_message',
                    'data': thread_dict
                }
            )
        self.send(text_data=json.dumps(
            form.errors
        ))

    def chat_message(self, event):
        print(event)
        self.send(text_data=json.dumps(
            event['data']
        ))
