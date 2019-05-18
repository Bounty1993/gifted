from datetime import datetime, timedelta
from django import forms

from .models import Room, Donation


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
        to_collect = cleaned_data['to_collect']
        if to_collect:
            raise forms.ValidationError('to_collect field should be empty by now')


class DonateForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea({'rows':5}),
        help_text='Jeśli chcesz możesz przekazać informacje obdarowanemu',
    )

    class Meta:
        model = Donation
        fields = [
            'amount',
            'comment',
        ]
        help_texts = {
            'amount': 'Minimalna wielkośc składki to 1 PLN',
        }

    def clean_donation(self):
        amount = self.cleaned_data['amount']
        minimal_amount = 1
        if amount < minimal_amount:
            err = f'You inserted amount {amount:.2f}. It is not enough. Minimal value is 1 PLN'
            raise forms.ValidationError(err)
        return amount
