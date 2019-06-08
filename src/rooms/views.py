from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
)
from .models import Room, Donation
from .forms import RoomRegisterForm, DonateForm, RoomUpdateForm, VisibleForm
import json

User = get_user_model()


class RoomRegisterView(CreateView):
    model = Room
    template_name = 'rooms/register.html'
    form_class = RoomRegisterForm

    def form_valid(self, form):
        room = form.save(commit=False)
        room.to_collect = room.price
        room.creator = self.request.user
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


class OwnerRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = self.request.user
        room = get_object_or_404(Room, pk=pk)
        if room.user == user:
            return redirect('rooms:list')
        super().dispath(request, *args, **kwargs)


class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def observers(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        user_id = request.user.id
        if user_id:
            message = room.add_observer(user_id=user_id)
            return JsonResponse(message)
        message = {'message': 'Użytkownik nie zalogowany. Proszę zaloguj się'}
        return JsonResponse(message)


class RoomUpdateView(UserPassesTestMixin, UpdateView):
    model = Room
    template_name = 'rooms/edit.html'
    form_class = RoomUpdateForm

    def test_func(self):
        pk = self.kwargs['pk']
        room = get_object_or_404(Room, pk=pk)
        return room.creator == self.request.user


def guests(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        json_data = json.loads(request.body)
        user = User.objects.filter(username=json_data.get('guest'))
        if user.count() != 1:
            message = {
                'error': 'Podany użytkownik nie istnieje'
            }
            return JsonResponse(message)
        user = user.first()
        data = {'guests': [user.id]}
        if json_data.get('type') == 'remove':
            guest_name = json_data.get('guest')
            message = room.guest_remove(guest_name)
            return JsonResponse(message)
        if json_data.get('type') == 'add':
            form = VisibleForm(data, instance=room)
            if form.is_valid():
                room.guests.add(user.id)
                room.save()
                message = {
                    'guests': room.get_guests()
                }
                return JsonResponse(message)
            message = {
                'error': 'Błędna nazwa użytkownika'
            }
            return JsonResponse(message)


@login_required
@transaction.atomic
def make_donation(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        form = DonateForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            comment = form.cleaned_data.get('comment')
            data = {
                'user': request.user,
                'amount': amount,
                'comment': comment
            }
            room.donate(data)
            success_msg = f'Dziękujemy ci {request.user.username} za wsparcie'
            messages.success(request, success_msg)
            return JsonResponse({'message': 'Success'})
        else:
            error_msg = f'Coś poszło nie tak. Zapoznaj się z błedami niżej'
            messages.warning(request, error_msg)
            return JsonResponse({'message': 'Error'})


class DonationListView(View):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if not room.is_visible():
            raise Http404()
        donations = list(room.objects.values_list(flat=True))
        if donations:
            message={
                'donations': donations
            }
        else:
            message = {
                'error': 'Nie znaleziono żadnych donacji'
            }
        return JsonResponse(message)
