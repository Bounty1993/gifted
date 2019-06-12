from django.contrib import admin
from django.urls import path, include
from .views import (
    PostCreateView,
    PostListView,
    change_likes,
    PostUpdateView,
    ThreadCreateView
)

app_name = 'forum'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('<pk>/', PostListView.as_view(), name='list'),
    path('<pk>/create/', PostCreateView.as_view(), name='create'),
    path('<pk>/edit/<post_pk>/', PostUpdateView.as_view(), name='edit'),
    path('ajax/thread/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('ajax/<post_id>/<type>/', change_likes, name='js_change_likes'),
]