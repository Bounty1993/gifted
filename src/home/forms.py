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
