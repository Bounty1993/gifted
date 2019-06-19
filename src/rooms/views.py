import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (DonateForm, MessageForm, RoomRegisterForm, RoomUpdateForm,
                    VisibleForm)
from .models import Donation, Message, Room

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


class FilterSearchMixin:
    request = None
    model = None

    def get_queryset(self):
        queryset = super().get_queryset()
        field = self.request.GET.get('search', None)
        if field:
            queryset = queryset.search(field)
        order = self.request.GET.get('order', None)
        if order:
            queryset = queryset.order_by(order)
        return queryset


class RoomListView(FilterSearchMixin, ListView):
    queryset = Room.get_visible.all()
    template_name = 'rooms/list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('observers').prefetch_related('patrons')

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


class DonationListView(ListView):
    model = Donation
    template_name = 'rooms/donations.html'
    paginate_by = 10
    order_by = 'id'

    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = Donation.objects.filter(room_id=pk)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['donations'] = self.object_list.select_related('user__profile')
        context['room'] = Room.objects.get(pk=self.kwargs['pk'])
        return context


class DonationChartView(View):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        chart_data = room.donations.get_chart_data()
        chart_data = {
            'chart': {
                'type': 'column'
            },
            'title': {
                'text': 'Historia przekazywanych kwot'
            },
            'xAxis': {
                'categories': chart_data['categories']
            },
            'yAxis': {
                'min': 0,
                'title': {
                    'text': 'Kwota (PLN)'
                }
            },
            'series': [{
                'name': 'Donacje',
                'data': chart_data['data']
            }]
        }
        return JsonResponse(chart_data)


@login_required
def observers(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST' and request.is_ajax:
        user_id = request.user.id
        message = room.add_observer(user_id=user_id)
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
