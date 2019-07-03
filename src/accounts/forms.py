import datetime

from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from .models import Profile


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        label='Informacje o Tobie',
        widget=forms.Textarea(attrs={'rows': 6}),
        help_text='Pozwól nam się poznać. Napisz coś o sobie',
        required=False)
    date_birth = forms.DateField(
        input_formats=('%d/%m/%Y',),
        label='Data urodzenia', required=False)

    class Meta:
        model = Profile
        fields = [
            'bio',
            'date_birth',
        ]

    def __init__(self, *args, **kwargs):
        # method to improve - it doesnt work--------------------
        super().__init__(*args, **kwargs)
        date_birth = self.fields['date_birth']
        if date_birth.initial:
            date_birth.disabled = True

    def clean_date_birth(self):
        """
        Verification if the age is above 18. If not ValidationError.
        """
        date_birth = self.cleaned_data['date_birth']
        if date_birth:
            today = datetime.datetime.now().date()
            eighteen_year_age = datetime.date(
                (today.year-18),
                today.month,
                today.day
            )
            is_adult = self.cleaned_data['date_birth'] < eighteen_year_age
            if not is_adult:
                raise ValidationError('Podana data wskazuje, że nie jesteś dorosły.')

        return date_birth


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]

    def clean_email(self):
        """
        Email has to be unique. Works for creation and update.
        """
        email = self.cleaned_data['email']
        user_id = self.instance.id
        same_email = (
            User.objects.exclude(id=user_id)
                .filter(email=email)
                .exclude(Q(email__isnull=True) | Q(email=''))
        )
        if same_email.exists():
            msg = "Podany email jest niepoprawny"
            raise forms.ValidationError(msg)
        return email


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'maksymalnie 150 znaków'
        self.fields['password1'].help_text = 'Ustanów odpowienio silne hasło'
        self.fields['password2'].help_text = 'Powtórz dokładnie to samo hasło!'

    class Meta(UserCreationForm.Meta):
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:   # No email in form so nothing to check
            return email
        same_email = (
            User.objects.filter(email=email)
                .exclude(Q(email__isnull=True) | Q(email=''))
        )
        if same_email.exists():
            msg = "Podany email jest niepoprawny"
            raise forms.ValidationError(msg)
        return email


class CustomPasswordChangeForm(SetPasswordForm):
    """
    Class change default PasswordChangeView. Old password is not required.
    That is why i use SetPasswordForm and not PasswordChangeForm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = 'Pamiętaj o bezpieczeństwie'
        self.fields['new_password1'].label = 'Nowe hasło'
        self.fields['new_password2'].help_text = 'Powtórz dokładnie to samo hasło!'
        self.fields['new_password2'].label = 'Potwierdz hasło'
