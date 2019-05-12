from datetime import datetime, timedelta
from django import forms

from .models import Room


class RoomRegisterForm(forms.ModelForm):

    date_expires = forms.DateField(input_formats=('%d/%m/%Y',))
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Room
        fields = [
            'receiver',
            'gift',
            'price',
            'description',
            'to_collect',
            'visible',
            'date_expires'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_collect'].widget = forms.HiddenInput()
        self.fields['to_collect'].required = False

    def clean_date_expires(self):
        date_expires = self.cleaned_data['date_expires']
        print(date_expires, 'clean_date')
        today = datetime.now().date()
        half_year_later = today + timedelta(days=183)
        if date_expires > half_year_later:
            raise forms.ValidationError('Date expires must not be more than 183 days from now')
        if date_expires <= today:
            raise forms.ValidationError('Date expires must be in the future')
        return date_expires

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data['date_expires'], 'clean')
        to_collect = cleaned_data['to_collect']
        if to_collect:
            raise forms.ValidationError('to_collect field should be empty by now')


class DonateForm(forms.ModelForm):
    donation = forms.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = Room
        fields = [
            'donation',
        ]

    def clean_donation(self):
        donation = self.cleaned_data['donation']
        minimal_amount = 1
        if donation < minimal_amount:
            err = f'You inserted amount {donation:.2f}. It is not enough. Minimal value is 1 PLN'
            raise forms.ValidationError(err)
        return donation
