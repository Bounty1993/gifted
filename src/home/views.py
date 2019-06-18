from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, FormView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .forms import ContactForm

User = get_user_model()


class MainView(TemplateView):
    template_name = 'home/main.html'


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'home/contact.html'

    def form_valid(self, form):
        form.send_mail()
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
        msg = {'is_taken': 'true'}
        if users.exists():
            msg = {'is_taken': 'false'}
            return JsonResponse(msg)
        return JsonResponse(msg)
