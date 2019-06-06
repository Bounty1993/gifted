from django.urls import path, include
from .views import (
    RoomRegisterView,
    RoomListView,
    RoomDetailView,
    RoomUpdateView,
    guests,
    donate,
)

app_name = 'rooms'
urlpatterns = [
    path('', RoomListView.as_view(), name='list'),
    path('register/', RoomRegisterView.as_view(), name='register'),
    path('<pk>/', RoomDetailView.as_view(), name='detail'),
    path('<pk>/edit/', RoomUpdateView.as_view(), name='edit'),
    path('<pk>/guests/', guests, name='edit'),
    path('<pk>/donate/', donate, name='donate'),
]