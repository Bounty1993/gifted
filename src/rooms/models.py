from django.conf import settings
from django.urls import reverse
from django.db import models
from django.core import serializers
from django.db.models import Q, Count, F, Sum


class VisibleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(visible=True)

    def search(self, field):
        return self.get_queryset().filter(
            Q(receiver__icontains=field) |
            Q(gift__icontains=field) |
            Q(description__icontains=field)
        )

    def most_popular(self):
        popular = (self.get_queryset()
                   .annotate(collected=F('price')-F('to_collect'))
                   .order_by('-collected')
                   )
        return popular

    def most_patrons(self):
        num_patrons = (self.get_queryset()
                       .annotate(num_patrons=Count('patrons'))
                       .exclude(num_patrons=0)
                       .order_by('-num_patrons')
                       )
        return num_patrons

    def most_to_collect(self):
        return self.get_queryset().order_by('-to_collect')


class Room(models.Model):
    receiver = models.CharField(max_length=50)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='rooms',
        null=True,
        blank=True,
    )
    gift = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.CharField(max_length=250)
    to_collect = models.DecimalField(max_digits=11, decimal_places=2)
    visible = models.BooleanField()
    date_expires = models.DateField()
    is_active = models.BooleanField(default=True)
    guests = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='guest_rooms',
    )
    patrons = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        through='Donation'
    )

    objects = models.Manager()
    get_visible = VisibleManager()

    def __str__(self):
        return f'{self.receiver} - {self.gift}'
    """
    def get_absolute_url(self):
        return reverse('rooms:detail', kwargs={'pk': self.id})
    """

    def is_visible(self):
        return self.visible

    def donate(self, data):
        try:
            user = data['user']
            amount = data['amount']
        except KeyError as err:
            raise AttributeError(f'no data for user or amount. Whole error: {err}')
        date = data.get('date', None)
        comment = data.get('comment', '')
        actual_amount = amount if amount < self.to_collect else self.to_collect
        full_collection = self.to_collect <= amount
        if full_collection:
            self.to_collect = 0
            self.is_active = False
        else:
            self.to_collect -= amount
        donation = Donation(
            user=user,
            room=self,
            date=date,
            amount=actual_amount,
            comment=comment
        )
        donation.save()
        self.save()

    def get_patrons(self):
        patrons = (
            self.donations.values_list('user__username', flat=True)
            .annotate(total_amount=Sum('amount'))
            .order_by('-total_amount')
        )
        return patrons

    def guest_remove(self, guest_name):
        guest = self.guests.filter(username=guest_name)
        if guest.count() != 1:
            return {'error': 'Nie ma takiego użytkownika'}
        self.guests.remove(guest.first())
        return self.get_guests_dict()

    def get_guests_dict(self):
        guests = self.guests.values_list('username', flat=True)
        guests_list = [guest for guest in guests]
        return guests_list

    def collected(self):
        return self.price - self.to_collect


class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='donations')
    date = models.DateField(auto_now=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f'{self.room} - {self.amount}'
