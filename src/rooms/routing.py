from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/room/<room_id>/donate/', consumers.DonateConsumer),
]
