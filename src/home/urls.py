from django.urls import include, path

from .views import ContactView, GetEmail, MainView, ValidateEmailView

app_name = 'home'
urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('ajax/<pk>/email/', GetEmail.as_view(), name='get_email'),
    path('ajax/email/<email>/validate', ValidateEmailView.as_view(), name='validate_email'),
]
