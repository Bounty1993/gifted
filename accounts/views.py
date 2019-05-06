from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

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
            return redirect('great/')
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
            messages.success(request, 'The profile was updated successfully')
            return redirect('success/')
        else:
            messages.error(request, 'The profile was not created')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/update.html', context=context)
