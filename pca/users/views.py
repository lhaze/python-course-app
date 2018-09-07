from django.contrib.auth import views as auth_views
from django.views import generic as generic_views

from . import forms


class LoginView(auth_views.LoginView):
    form_class = forms.AuthenticateForm
    template_name = 'users/login.j2'


class RegisterView(generic_views.CreateView):
    form_class = forms.UserCreateForm
    template_name = 'users/register.j2'
