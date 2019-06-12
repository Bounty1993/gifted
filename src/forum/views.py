import json
from django.shortcuts import (
    redirect,
    get_object_or_404
)
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views import View
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView
)
from src.rooms.models import Room
from .models import Post, Thread
from .forms import (
    PostCreateForm,
    PostUpdateForm,
    ThreadCreateForm,
)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs['pk']
        context['room'] = get_object_or_404(Room, id=room_id)
        return context


class PostListView(ListView):
    model = Post
    template_name = 'forum/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        room_id = self.kwargs.get('pk')
        queryset = Post.visible.filter(room__id=room_id)
        return queryset.summarise()


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


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'forum/update.html'
    form_class = PostUpdateForm

    def get_object(self):
        post_pk = self.kwargs['post_pk']
        obj = get_object_or_404(Post, pk=post_pk)
        return obj


class ThreadCreateView(View):
    def post(self, request):
        if request.is_ajax():
            data = json.loads(request.body)
            print(data)
            post = get_object_or_404(Post, pk=int(data['post_id']))
            author = request.user.id
            print(author)
            data.update({
                'post': post,
                'author': author
            })
            form = ThreadCreateForm(data)
            if form.is_valid():
                msg = {'is_valid': 'true'}
                return JsonResponse(msg)
            msg = {
                'is_valid': 'false',
                'error': form.errors,
            }
            return JsonResponse(msg)


class DeleteThread(View):
    def delete(self, request, pk):
        if request.is_ajax():
            thread = get_object_or_404(Thread, pk=pk)
            author = request.user
            if not author == thread:
                msg = {
                    'is_valid': 'false',
                    'error': 'Użytkownik nie jest autorem'
                }
                return JsonResponse(msg)
            thread.delete()
            msg = {'is_valid': 'true'}
            return JsonResponse(msg)
