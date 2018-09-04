from django.contrib.auth.views import LoginView as AuthLoginView

from . import forms


class LoginView(AuthLoginView):
    form_class = forms.AuthenticationForm
    template_name = 'auth/login.j2'
