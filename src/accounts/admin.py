from django.contrib import admin

from src.forum.models import Post, Thread
from src.rooms.models import Donation, Message, Room

from .models import Profile

admin.site.register([Room, Donation, Message, Profile, Post, Thread])
