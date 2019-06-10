from django.conf import settings
from django.db import models
from src.rooms.models import Room


class Post(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET('Konto usunięte')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    subject = models.CharField('Tytuł', max_length=100)
    content = models.CharField('Treść', max_length=500)
    likes = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

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


class Thread(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    subject = models.CharField('Tytuł', max_length=100)
    content = models.CharField('Treść', max_length=500)
    likes = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
