from django.urls import path, include
from .views import (
    MainView,
    ContactView,
    GetEmail,
    ValidateEmailView
)

app_name = 'home'
urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('ajax/<pk>/email/', GetEmail.as_view(), name='get_email'),
    path('ajax/email/<slug:email>/validate', ValidateEmailView.as_view(), name='validate_email'),
]
