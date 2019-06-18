from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from src.home.forms import send_email


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    bio = models.CharField(max_length=250, blank=True)
    date_birth = models.DateField(null=True, blank=True)

    @property
    def full_name(self):
        full_name = self.user.get_full_name()
        if not full_name:
            return self.user.username
        return full_name

    def get_observed_rooms(self):
        observed_rooms = self.user.observed_rooms
        ordered_rooms = observed_rooms.order_by_score()
        return ordered_rooms

# receiver by zapisać i utworzyć Profile po zmianach w User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        username = instance.username
        email = instance.email
        subject = f'Witaj {username} Założyłeś właśnie konto w Gifted'
        message = 'Dziękujemy za zaufanie. Będziemy szcześliwi jeśli polecisz nas znajomym'
        data = {'subject': subject, 'message': message, 'to': email}
        send_email(data)

# ----------------------------------------------------------
