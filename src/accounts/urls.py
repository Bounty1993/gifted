from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path, re_path

from .views import (MyPasswordChangeView, CustomPasswordResetView,
                    CustomPasswordResetFromKeyView, ProfileDetailView,
                    signup, update_profile)

app_name = 'accounts'
urlpatterns = [
    path('', ProfileDetailView.as_view(), name='home'),
    path('signup/', signup, name='signup'),
    path('login/',
         LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('update/', update_profile, name='update'),
    path('password/change/', MyPasswordChangeView.as_view(), name='change_password'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='reset_password'),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            CustomPasswordResetFromKeyView.as_view(), name='account_reset_password_from_key'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
