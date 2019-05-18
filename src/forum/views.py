from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.generic import (
    CreateView,
    ListView,
    DetailView
)
from src.rooms.models import Room
from .models import Post
from .forms import PostCreateForm


class PostCreateView(CreateView):
    model = Post
    template_name = 'forum/post_create.html'
    form_class = PostCreateForm

    def form_valid(self, form):
        post = form.save(commit=False)
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        post.room = room
        post.user = self.request.user
        post.save()
        msg_success = f'Dziękujemy za twój komentarz'
        messages.success(self.request, msg_success)
        return redirect(reverse('forum:list', kwargs={'pk': room_id}))


class PostListView(ListView):
    model = Post
    template_name = 'forum/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        room_id = self.kwargs.get('pk')
        queryset = Post.objects.filter(room__id=room_id)
        return queryset


def change_likes(request, post_id, type):
    user = request.POST.get('user', None)
    if not user:
        data = {
            'error', 'user is required'
        }
        return JsonResponse(data)
    post = Post.objects.filter(post_id)
    if post.count() != 1:
        data = {
            'error': 'Post id is not correct'
        }
        return JsonResponse(data)
    if type == 'like':
        post.add_like()
        data = {
            'likes': post.likes
        }
        return JsonResponse(data)
    post.add_dislike()
    data = {
        'likes': post.likes
    }
    return JsonResponse(data)