from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
import datetime


class VisibleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(visible=True)

    def search(self, field):
        return self.get_queryset().filter(
            Q(receiver__icontains=field) |
            Q(gift__icontains=field) |
            Q(description__icontains=field)
        )


class Room(models.Model):
    patrons = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    receiver = models.CharField(max_length=50)
    gift = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.CharField(max_length=250)
    to_collect = models.DecimalField(max_digits=11, decimal_places=2)
    visible = models.BooleanField()
    date_expires = models.DateField()

    get_visible = VisibleManager()

    def __str__(self):
        return f'{self.receiver} - {self.gift}'
    """
    def get_absolute_url(self):
        return reverse('rooms:detail', kwargs={'pk': self.id})
    """