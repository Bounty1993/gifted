from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.db.models import (
    Q, Count, F, Sum,
)


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
                       .annotate(patrons_number=Count('patrons'))
                       .exclude(patrons_number=0)
                       .order_by('-patrons_number')
                       )
        return num_patrons

    def most_to_collect(self):
        return self.get_queryset().order_by('-to_collect')


class Room(models.Model):
    receiver = models.CharField('odbiorca', max_length=50)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='rooms',
        null=True,
        blank=True,
    )
    gift = models.CharField('Cel', max_length=50)
    price = models.DecimalField('Cena', max_digits=11, decimal_places=2)
    description = models.CharField('Opis', max_length=250)
    to_collect = models.DecimalField('Do zebrania', max_digits=11, decimal_places=2)
    visible = models.BooleanField('Widoczny dla wszystkich?')
    date_expires = models.DateField('Data wygaśnięcia')
    is_active = models.BooleanField(default=True)
    score = models.FloatField(default=0)
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
    observers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='observed_rooms'
    )

    objects = models.Manager()
    get_visible = VisibleManager()

    @property
    def percent_left(self):
        return (self.to_collect / self.price) * 100

    @property
    def percent_got(self):
        return 100 - self.percent_left

    @property
    def num_patrons(self):
        return self.patrons.count()

    def __str__(self):
        return f'{self.receiver} - {self.gift}'

    """
    def get_absolute_url(self):
        return reverse('rooms:detail', kwargs={'pk': self.id})
    """

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def update_score(self):
        # It needs more development - unfortunately...
        # Problem is a recursion when signals
        patrons_rank = self.patrons.count() * 2
        observers_rank = self.observers.count()
        collected_rank = self.collected() / 1000
        total_rank = patrons_rank + observers_rank + collected_rank
        self.score = total_rank

    def is_visible(self):
        return self.visible

    def add_observer(self, user_id):
        try:
            self.observers.add(user_id)
        except ValueError:
            return {'message': 'Błędne dane!'}
        return {'message': 'Success'}

    def donate(self, data):
        try:
            user = data['user']
            amount = data['amount']
        except KeyError as err:
            return {'message': 'Brak wszystkich danych'}
        date = data.get('date', None)
        comment = data.get('comment', amount)
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
        return {'message': 'Success'}

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

    def all_likes(self):
        posts = self.posts
        likes_per_post = posts.data_with_likes()
        all_likes = likes_per_post.aggregate(Sum('all_likes'))
        return all_likes

    def all_comments(self):
        posts = self.posts
        num_threads = (
            posts
                .annotate(num_threads=Count('threads'))
                .aggregate(Sum(F'num_threads'))
        )
        return num_threads


class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='donations')
    date = models.DateField(auto_now=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f'{self.room} - {self.amount}'


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    subject = models.CharField('Tytuł', max_length=150)
    content = models.CharField('Treść', max_length=255)

    def __str__(self):
        return f'{self.receiver} - {self.subject}'
