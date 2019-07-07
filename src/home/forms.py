from django import forms
from django.core.mail import EmailMessage


# it will be shared task
def send_email(data):
    message = EmailMessage(data['subject'], data['message'], to=[data['to']])
    message.send()


class ContactForm(forms.Form):
    subject = forms.CharField(label='Tytuł', max_length=100)
    message = forms.CharField(label='Treść', max_length=250,
                              widget=forms.Textarea({'rows': 5}))
    email = forms.EmailField(label='Email')
