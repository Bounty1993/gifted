from django.conf import settings
from django.db import models
from src.rooms.models import Room


class PostQuerySet(models.QuerySet):
    def get_visible(self):
        return self.filter(room__visible=True)

    def summarise(self):
        all_comments = []
        for post in self.prefetch_related('threads').prefetch_related('author'):
            post_detail = {
                'id': post.id,
                'author': post.author,
                'subject': post.subject,
                'content': post.content,
                'likes': post.likes,
                'date': post.date,
                'threads': post.threads.count(),
            }
            all_comments.append(post_detail)
        return all_comments


class Post(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET('Konto usunięte')
    )
    subject = models.CharField('Tytuł', max_length=100)
    content = models.CharField('Treść', max_length=500)
    likes = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    visible = PostQuerySet.as_manager()
    objects = models.Manager()

    def __str__(self):
        return self.subject

    def has_parent(self):
        if self.parent:
            return True
        return False

    def add_like(self):
        self.likes += 1
        self.save()

    def add_dislike(self):
        self.likes -= 1
        self.save()


class ThreadQuerySet(models.QuerySet):
    def get_all_children(self):
        node = []
        for thread in self.filter(parent__isnull=True):
            data = thread.show_children()
            node.append(data)
        return node


class Thread(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='threads')
    subject = models.CharField('Tytuł', max_length=100)
    content = models.CharField('Treść', max_length=500)
    likes = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children'
    )

    objects = ThreadQuerySet.as_manager()

    def has_parent(self):
        if self.parent:
            return True
        return False

    def show_children(self):
        all_threads = []
        if not self.children.all():
            return all_threads
        for thread in self.children.all():
            all_threads.append({thread: thread.show_children()})
        return all_threads

    def add_like(self):
        self.likes += 1
        self.save()

    def add_dislike(self):
        self.likes -= 1
        self.save()
