import json
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
from .models import (
    Room,
    Donation,
    Message,
)
from .forms import (
    RoomRegisterForm,
    DonateForm,
    RoomUpdateForm,
    VisibleForm,
    MessageForm,
)

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
        queryset = Room.get_visible.order_by('-to_collect')
        if field:
            return queryset.search(field)
        return queryset

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
        donations = self.object.donations.select_related('user__profile')
        context['donations'] = donations
        context['users_list'] = User.objects.all()
        return context


@login_required
def observers(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        user_id = request.user.id
        if user_id:
            message = room.add_observer(user_id=user_id)
            return JsonResponse(message)
        message = {'message': 'Użytkownik nie zalogowany. Proszę zaloguj się'}
        return JsonResponse(message)


@login_required
def delete_observers(request):
    if request.method == 'POST' and request.is_ajax:
        data = json.loads(request.body)
        user = request.user
        room = user.observed_rooms.filter(id=data['id'])
        if room.count != 1:
            msg = {
                'is_valid': 'false',
                'error': 'Nie obserwujesz podanej zbiórki'
            }
            return JsonResponse(msg)
        room.first().delete()
        msg = {'is_valid': 'true'}
        return JsonResponse(msg)


class RoomUpdateView(UserPassesTestMixin, UpdateView):
    model = Room
    template_name = 'rooms/edit.html'
    form_class = RoomUpdateForm

    def test_func(self):
        pk = self.kwargs['pk']
        room = get_object_or_404(Room, pk=pk)
        return room.creator == self.request.user


@login_required
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
            message = {
                'guests': room.guest_remove(guest_name)
            }
            return JsonResponse(message)
        if json_data.get('type') == 'add':
            form = VisibleForm(data, instance=room)
            if form.is_valid():
                room.guests.add(user.id)
                room.save()
                message = {
                    'guests': room.get_guests_dict()
                }
                return JsonResponse(message)
            message = {
                'error': 'Błędna nazwa użytkownika'
            }
            return JsonResponse(message)


@login_required
def make_message(request):
    if request.method == 'POST' and request.is_ajax:
        data = json.loads(request.body)
        sender = request.user.id
        data.update({'sender': sender})
        form = MessageForm(data)
        if form.is_valid():
            form.save()
            message = {'is_valid': 'true'}
            return JsonResponse(message)
        message = {'is_valid': 'false', 'errors': form.errors}
        return JsonResponse(message)


@login_required
def delete_message(request):
    if request.method == 'POST' and request.is_ajax:
        data = json.loads(request.body)
        message = get_object_or_404(Message, id=data['id'])
        if message.receiver != request.user:
            msg = {
                'is_valid': 'false',
                'error': 'Nie jesteś upraniony do usuwania wiadomości'
            }
            return JsonResponse(msg)
        message.delete()
        msg = {'is_valid': 'true'}
        return JsonResponse(msg)


@login_required
@transaction.atomic
def make_donation(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        data = json.loads(request.body)
        form = DonateForm(data)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            comment = form.cleaned_data.get('comment')
            data = {
                'user': request.user,
                'amount': amount,
                'comment': comment
            }
            message = room.donate(data)
            messages.success(request, "Dziękujemy za twoje wsparcie")
            return JsonResponse(message)
        else:
            message = {'message': form.errors}
            return JsonResponse(message)


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
