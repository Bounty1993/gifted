import json
from django.shortcuts import (
    render,
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


class AllPostListView(ListView):
    model = Post
    template_name = 'forum/all_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        field = self.request.GET.get('search', None)
        if field:
            queryset = (
                Post.visible
                    .search(field=field)
                    .data_with_likes()
                    .select_related('author')
                    .prefetch_related('threads')
            )
            return queryset
        queryset = (
            Post.visible
                .data_with_likes()
                .select_related('author')
                .prefetch_related('threads')
        )
        return queryset


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('pk')
        room = get_object_or_404(Room, pk=room_id)
        context['room'] = room
        context['all_likes'] = room.all_likes()
        context['all_comments'] = room.all_comments()
        return context


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

    def get_success_url(self):
        room = self.object.room
        return redirect(room)


class PostDeleteView(View):
    def delete(self, request, pk, post_pk):
        if request.is_ajax():
            post = get_object_or_404(Post, pk=post_pk)
            user = request.user
            author = post.author
            print(author, )
            if not user == author:
                msg = {
                    'is_valid': 'false',
                    'error': 'Użytkownik nie jest autorem'
                }
                return JsonResponse(msg)
            # post.delete()
            msg = {'is_valid': 'true'}
            return JsonResponse(msg)


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
