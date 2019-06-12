from django.contrib import admin
from django.urls import path, include
from .views import (
    PostCreateView,
    PostListView,
    PostUpdateView,
    ThreadCreateView,
    AddLikeView,
    AddDisLikeView,

)

app_name = 'forum'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('<pk>/', PostListView.as_view(), name='list'),
    path('<pk>/create/', PostCreateView.as_view(), name='create'),
    path('<pk>/edit/<post_pk>/', PostUpdateView.as_view(), name='edit'),
    path('ajax/thread/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('ajax/like/', AddLikeView.as_view(), name='add_like'),
    path('ajax/dislike/', AddDisLikeView.as_view(), name='add_dislike'),

]