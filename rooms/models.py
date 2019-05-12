from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
import datetime

from accounts.models import Profile


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
    receiver = models.CharField(max_length=50)
    gift = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.CharField(max_length=250)
    to_collect = models.DecimalField(max_digits=11, decimal_places=2)
    visible = models.BooleanField()
    date_expires = models.DateField()
    is_active = models.BooleanField(default=True)
    patrons = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, through='Donation')

    objects = models.Manager()
    get_visible = VisibleManager()

    def __str__(self):
        return f'{self.receiver} - {self.gift}'
    """
    def get_absolute_url(self):
        return reverse('rooms:detail', kwargs={'pk': self.id})
    """

    def donate(self, data):
        try:
            user = data['user']
            amount = data['amount']
        except KeyError as err:
            raise AttributeError(f'no data for user or amount. Whole error: {err}')
        date = data.get('date', None)
        comment = data.get('comment', '')
        actual_amount = amount if amount < self.to_collect else self.to_collect
        full_collection = self.to_collect < amount
        if full_collection:
            self.to_collect = 0
            self.is_active = False
        else:
            self.collect -= amount
        profile = Profile.objects.get(user=user)
        donation = Donation(
            profile=profile,
            date=date,
            amount=actual_amount,
            comment=comment
        )
        donation.save()
        self.patrons.add(donation)
        self.save()

    def get_patrons(self):
        pass


class Donation(models.Model):
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=50, blank=True)