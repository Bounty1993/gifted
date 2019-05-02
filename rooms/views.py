from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    ListView,
    DetailView
)
from .models import Room
from .forms import RoomRegisterForm


class RoomRegisterView(CreateView):
    model = Room
    template_name = 'rooms/register.html'
    form_class = RoomRegisterForm
    success_url = 'rooms/list/'

    def form_valid(self, form):
        room = form.save(commit=False)
        room.to_collect = room.price
        room.save()
        return redirect(self.get_success_url())


class RoomListView(ListView):
    model = Room
    template_name = 'rooms/list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.filter(visible=True)


class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/detail.html'


