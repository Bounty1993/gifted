from django.urls import path, include
from .views import (
    RoomRegisterView,
    RoomListView,
    RoomDetailView,
    RoomUpdateView,
    observers,
    guests,
    make_message,
    make_donation,
)

app_name = 'rooms'
urlpatterns = [
    path('', RoomListView.as_view(), name='list'),
    path('register/', RoomRegisterView.as_view(), name='register'),
    path('<pk>/', RoomDetailView.as_view(), name='detail'),
    path('<pk>/edit/', RoomUpdateView.as_view(), name='edit'),
    path('<pk>/guests/', guests, name='edit'),

    path('ajax/message/', make_message, name='message'),
    path('<pk>/ajax/donate/', make_donation, name='donate'),
    path('<pk>/ajax/observers/', observers, name='observers'),
]