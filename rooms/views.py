from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    ListView,
    DetailView
)
from accounts.models import Profile
from .models import Room
from .forms import RoomRegisterForm, DonateForm


class RoomRegisterView(CreateView):
    model = Room
    template_name = 'rooms/register.html'
    form_class = RoomRegisterForm

    def form_valid(self, form):
        room = form.save(commit=False)
        room.to_collect = room.price
        room.save()
        return redirect(reverse('rooms:list'))


class RoomListView(ListView):
    model = Room
    template_name = 'rooms/list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        field = self.request.GET.get('search', None)
        if field:
            return Room.get_visible.search(field)
        return Room.get_visible.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_popular'] = Room.get_visible.most_popular()
        context['most_patrons'] = Room.get_visible.most_patrons()
        context['most_to_collect'] = Room.get_visible.most_to_collect()
        return context


class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/detail.html'


def donate(request, pk):

    room = get_object_or_404(Room, pk=pk)

    form = DonateForm()
    context = {
        'form': form,
        'room': room
    }
    return render(request, 'rooms/donate.html', context=context)
