from django import forms
from django.core.mail import EmailMessage


# it will be shared task
def send_email(data):
    message = EmailMessage(data['subject'], data['message'], to=[data['to']])
    message.send()


class ContactForm(forms.Form):
    user = forms.IntegerField(required=False)
    subject = forms.CharField(label='tytuł', max_length=100)
    message = forms.CharField(label='treść', max_length=250)
    email = forms.EmailField(label='email', required=False)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data['user']
        email = cleaned_data['email']
        if not (user or email):
            raise forms.ValidationError(
                'Błedne dane. Zdefinuj formę kontaktu.'
                'Zaloguj się lub podaj email'
            )
    """
    def send_email(self):
        cleaned_data = self.clean()
        print(cleaned_data)
        email = cleaned_data['email']
        if cleaned_data['user']:
            email = cleaned_data['user']
        data = {
            'subject': cleaned_data['subject'],
            'message': cleaned_data['message'],
            'to': email
        }
        send_email(data)  # will be delayed
    """
