from django.urls import include, path

from .views import (DonationChartView, DonationListView, RoomDetailView,
                    RoomEditView, RoomListView, RoomRegisterView,
                    delete_message, delete_observers, guests, make_message,
                    observers)

app_name = 'rooms'
urlpatterns = [
    path('', RoomListView.as_view(), name='list'),
    path('register/', RoomRegisterView.as_view(), name='register'),
    path('<int:pk>/', RoomDetailView.as_view(), name='detail'),
    path('<int:pk>/donations/', DonationListView.as_view(), name='donation'),
    path('<int:pk>/edit/', RoomEditView.as_view(), name='edit'),

    path('<int:pk>/ajax/guests/', guests, name='guests'),
    path('ajax/message/', make_message, name='message'),
    path('ajax/message/delete/', delete_message, name='message_delete'),
    path('<int:pk>/ajax/donations/charts', DonationChartView.as_view(), name='donation_chart'),
    path('<int:pk>/ajax/observers/', observers, name='observers'),
    path('ajax/observers/delete', delete_observers, name='observers_delete')
]
