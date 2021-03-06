from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from .forms import ContactForm, send_email

User = get_user_model()


class MainView(TemplateView):
    template_name = 'home/main.html'


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'home/contact.html'
    success_url = reverse_lazy('home:main')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial.update({
                'email': user.email
            })
        return initial

    def form_valid(self, form):
        # form.send_email()
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        data = {
            'subject': subject,
            'message': message,
            'to': email
        }
        send_email(data)
        messages.success(self.request, 'Dziękujemy za pytanie')
        return super().form_valid(form)


class GetEmail(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=int(pk))
        message = {
            'pk': pk,
            'email': user.email
        }
        return JsonResponse(message)


class ValidateEmailView(View):
    def get(self, request, email):
        users = User.objects.filter(email=email)
        msg = {'is_taken': 'false'}
        if users.exists():
            msg = {'is_taken': 'true'}
        return JsonResponse(msg)
