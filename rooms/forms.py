from datetime import datetime, timedelta
from django import forms

from .models import Room


class RoomRegisterForm(forms.ModelForm):

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
        today = datetime.now().date()
        half_year_later = today + timedelta(days=183)
        if date_expires > half_year_later:
            raise forms.ValidationError('Date expires must not be more than 183 days from now')
        if date_expires <= today:
            raise forms.ValidationError('Date expires must be in the future')

