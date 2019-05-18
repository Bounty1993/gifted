from django.urls import path, include
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)
from .views import (
    ProfileDetailView,
    signup,
    update_profile,
    MyPasswordChangeView,
)

app_name = 'accounts'
urlpatterns = [
    path('', ProfileDetailView.as_view(), name='main'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('update/', update_profile, name='update'),
    path('change_password/', MyPasswordChangeView.as_view(), name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
]