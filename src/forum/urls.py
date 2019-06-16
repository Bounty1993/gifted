from django.contrib import admin
from django.urls import path, include
from .views import (
    AllPostListView,
    PostCreateView,
    PostListView,
    PostUpdateView,
    PostDeleteView,
    ThreadCreateView,
    GetThreadsView,
    AddLikeView,
    AddDisLikeView,

)

app_name = 'forum'
urlpatterns = [
    path('', AllPostListView.as_view(), name='all'),
    path('<pk>/', PostListView.as_view(), name='list'),
    path('<pk>/create/', PostCreateView.as_view(), name='create'),
    path('<pk>/edit/<post_pk>/', PostUpdateView.as_view(), name='edit'),
    path('<pk>/delete/<post_pk>/', PostDeleteView.as_view(), name='delete'),
    path('<pk>/ajax/thread/list/', GetThreadsView.as_view(), name='thread_list'),
    path('ajax/thread/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('ajax/like/', AddLikeView.as_view(), name='add_like'),
    path('ajax/dislike/', AddDisLikeView.as_view(), name='add_dislike'),

]