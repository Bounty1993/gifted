from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from allauth.account.views import PasswordResetView, PasswordResetFromKeyView

from src.rooms.models import Room
from .forms import ProfileForm, UserUpdateForm, CustomPasswordChangeForm, CustomUserCreationForm
from .models import Profile


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = Profile.objects.filter(user=user)
            profile.update(
                bio=profile_form.cleaned_data['bio'],
                date_birth=profile_form.cleaned_data['date_birth']
            )
            messages.success(request, 'Profil został utworzony pomyślnie')
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
            return redirect(reverse_lazy('accounts:home'))
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileForm()
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/signup.html', context=context)


class SearchOrderProfileMixin:
    object = None
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = self.object.observed_rooms.all()
        context['observed'] = rooms.count()
        is_all = self.request.GET.get('all', None)
        if not rooms.exists() or is_all == 'true':
            rooms = Room.get_visible.all()
        order = self.request.GET.get('order', '')
        if order in ['most_popular', 'most_patrons', 'most_to_collect']:
            rooms = getattr(rooms, order)()

        rooms = rooms.prefetch_related('creator')

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
    model = get_user_model()
    template_name = 'accounts/home.html'
    context_object_name = 'profile'
    paginate_by = 3

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_list'] = self.object.messages.all()
        context['full_name'] = self.object.profile.full_name
        return context


@login_required
@transaction.atomic
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil został pomyślnie zaaktualizowany')
            return redirect(reverse_lazy('accounts:home'))
        else:
            messages.error(request, 'Profil nie został utworzony')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/update.html', context=context)


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = CustomPasswordChangeForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Hasło zostało zmienione pomyślnie')
        update_session_auth_hash(self.request, form.user)
        return redirect(reverse_lazy('accounts:home'))


class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/password_reset.html'

    def form_valid(self, form):
        msg = """Na twoją skrzynkę mailową zostały wysłane wszystkie 
        informacje potrzebne do zrestartowania hasła. Postępuj wedle instrukcji."""
        messages.success(self.request, msg)
        return super().form_valid(form)


class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:home')
