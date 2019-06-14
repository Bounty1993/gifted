import json
from django.shortcuts import (
    redirect,
    get_object_or_404
)
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
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
        post.author = self.request.user
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


class AddLikeView(View):
    def post(self, request):
        data = json.loads(request.body)
        pk = int(data['id'])
        is_thread = data.get('is_thread', None)
        msg = {'success': 'true'}
        if is_thread is not None:
            thread = get_object_or_404(Thread, pk=pk)
            thread.add_like()
            num_likes = {
                'num_likes': thread.likes
            }
            msg.update(num_likes)
            return JsonResponse(msg)
        post = get_object_or_404(Post, pk=pk)
        post.add_like()
        num_likes = {
            'num_likes': post.likes
        }
        msg.update(num_likes)
        return JsonResponse(msg)


class AddDisLikeView(View):
    def post(self, request):
        data = json.loads(request.body)
        pk = int(data['id'])
        is_thread = data.get('is_thread', None)
        msg = {'success': 'true'}
        if is_thread is not None:
            thread = get_object_or_404(Thread, pk=pk)
            thread.add_dislike()
            num_likes = {
                'num_likes': thread.likes
            }
            msg.update(num_likes)
            return JsonResponse(msg)
        post = get_object_or_404(Post, pk=pk)
        post.add_dislike()
        num_likes = {
            'num_likes': post.likes
        }
        msg.update(num_likes)
        return JsonResponse(msg)


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'forum/update.html'
    form_class = PostUpdateForm

    def get_object(self):
        post_pk = self.kwargs['post_pk']
        obj = get_object_or_404(Post, pk=post_pk)
        return obj


class GetThreadsView(View):
    def post(self, request, pk):
        data = json.loads(request.body)
        post_id = data.get('post_id', None)
        if post_id:
            threads = Thread.objects.get_main(post_id=post_id)
            message = {
                'is_valid': 'true',
                'threads': threads
            }
            return JsonResponse(message)
        thread_id = data['thread_id']
        threads = Thread.objects.get_secondary(thread_id=thread_id)
        message = {
            'is_valid': 'true',
            'threads': threads,
        }
        return JsonResponse(message)


class ThreadCreateView(View):
    def post(self, request):
        if request.is_ajax():
            data = json.loads(request.body)
            post = get_object_or_404(Post, pk=int(data['post_id']))
            author = request.user.id
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
