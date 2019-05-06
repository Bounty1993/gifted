from django.urls import path, include
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)
from .views import (
    signup,
    update_profile
)

app_name = 'accounts'
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('update/', update_profile, name='update'),
    path('logout/', LogoutView.as_view(), name='logout')
]