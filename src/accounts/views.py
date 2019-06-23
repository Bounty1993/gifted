from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from src.rooms.models import Room

from .forms import ProfileForm, UserForm
from .models import Profile


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_instance = user_form.save()
            profile_instance = Profile.objects.filter(user=user_instance)
            profile_instance.update(
                bio=profile_form.cleaned_data['bio'],
                date_birth=profile_form.cleaned_data['date_birth']
            )
            messages.success(request, 'The profile was created successfully')
            return redirect(reverse_lazy('accounts:home'))
        else:
            messages.error(request, 'The profile was not created')
    else:
        user_form = UserCreationForm()
        profile_form = ProfileForm()
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/signup.html', context=context)


class SearchOrderProfileMixin:
    object = None
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = self.object.user.observed_rooms.all()
        context['observed'] = rooms.count()
        is_all = self.request.GET.get('all', None)
        if not rooms.exists() or is_all == 'true':
            rooms = Room.get_visible.all()
        order = self.request.GET.get('order', None)
        if order == 'most_popular':
            rooms = rooms.most_popular()
        elif order == 'most_patrons':
            rooms = rooms.most_patrons()
        elif order == 'most_to_collect':
            rooms = rooms.most_to_collect()

        paginator = Paginator(rooms, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            rooms_list = paginator.page(page)
        except PageNotAnInteger:
            rooms_list = paginator.page(1)
        except EmptyPage:
            rooms_list = paginator.page(paginator.num_pages)
        context['rooms'] = rooms_list
        return context


class ProfileDetailView(LoginRequiredMixin, SearchOrderProfileMixin, DetailView):
    model = Profile
    template_name = 'accounts/home.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_list'] = self.object.user.messages.all()
        return context


@login_required
@transaction.atomic
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil został utworzony pomyślnie')
            return redirect(reverse_lazy('accounts:home'))
        else:
            messages.error(request, 'Profil nie został utworzony')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/update.html', context=context)


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Hasło zostało zmienione pomyślnie')
        update_session_auth_hash(self.request, form.user)
        return redirect(reverse_lazy('accounts:home'))
