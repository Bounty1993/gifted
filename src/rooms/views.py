from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.views.generic import (
    CreateView,
    ListView,
    DetailView
)
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


@login_required
@transaction.atomic
def donate(request, pk):

    room = get_object_or_404(Room, pk=pk)

    if request.method=='POST':
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
            success_msg = f'Dziękujemy ci {request.user.full_name} za wsparcie'
            messages.success(request, success_msg)
            return redirect('rooms:detail', kwargs={'pk': pk})
        else:
            error_msg = f'Coś poszło nie tak. Zapoznaj się z błedami niżej'
            messages.error(request, error_msg)

    form = DonateForm()
    context = {
        'form': form,
        'room': room
    }
    return render(request, 'rooms/donate.html', context=context)
