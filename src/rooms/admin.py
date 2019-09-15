from django.contrib import admin

from .models import Room, Donation, Message

admin.register(Room, Donation, Message)
