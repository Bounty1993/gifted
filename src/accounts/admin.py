from django.contrib import admin

from src.rooms.models import Room, Donation, Message
from .models import Profile
from src.forum.models import Post

admin.site.register([Room, Donation, Message, Profile, Post])
