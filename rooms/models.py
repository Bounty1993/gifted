from django.conf import settings
from django.db import models
import datetime


class Room(models.Model):
    patrons = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    receiver = models.CharField(max_length=50)
    gift = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.CharField(max_length=250)
    to_collect = models.DecimalField(max_digits=11, decimal_places=2)
    visible = models.BooleanField()
    date_expires = models.DateField()

    def __str__(self):
        return f'{self.receiver} - {self.gift}'
