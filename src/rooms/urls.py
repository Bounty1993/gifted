from django.urls import path, include
from .views import (
    RoomRegisterView,
    RoomListView,
    RoomDetailView,
    DonationListView,
    DonationChartView,
    RoomUpdateView,
    observers,
    delete_observers,
    guests,
    make_message,
    delete_message,
    make_donation,
)

app_name = 'rooms'
urlpatterns = [
    path('', RoomListView.as_view(), name='list'),
    path('register/', RoomRegisterView.as_view(), name='register'),
    path('<pk>/', RoomDetailView.as_view(), name='detail'),
    path('<pk>/donations/', DonationListView.as_view(), name='donation'),
    path('<pk>/edit/', RoomUpdateView.as_view(), name='edit'),

    path('<pk>/ajax/guests/', guests, name='edit'),
    path('ajax/message/', make_message, name='message'),
    path('ajax/message/delete/', delete_message, name='message_delete'),
    path('<pk>/ajax/donate/', make_donation, name='donate'),
    path('<pk>/ajax/donations/charts', DonationChartView.as_view(), name='donation_chart'),
    path('<pk>/ajax/observers/', observers, name='observers'),
    path('ajax/observers/delete', delete_observers, name='observers_delete')
]