from django.urls import path, include
from .views import (
    RoomRegisterView,
    RoomListView,
    RoomDetailView,
    donate
)

app_name = 'rooms'
urlpatterns = [
    path('', RoomListView.as_view(), name='list'),
    path('register/', RoomRegisterView.as_view(), name='register'),
    path('<pk>/', RoomDetailView.as_view(), name='detail'),
    path('<pk>/donate', donate, name='donate'),
]