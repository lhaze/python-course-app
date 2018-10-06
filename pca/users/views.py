from django.conf import settings
from django.contrib.auth import (
    login as auth_login,
    views as auth_views,
)
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy

from pca.users import signals
from pca.utils.request import get_request_scheme
from pca.utils.signal import BoundSignal
from pca.utils.views import CommandGetView, CommandView
from . import forms, services


class LoginView(auth_views.LoginView):
    form_class = forms.AuthenticateForm
    template_name = 'users/login.j2'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.user)
        return HttpResponseRedirect(self.get_success_url())


class RegisterView(CommandView):

    request = None
    login_required = False
    form_class = forms.UserCreateForm
    template_name = 'users/register.j2'
    success_url = settings.LOGIN_REDIRECT_URL
    disallowed_url = reverse_lazy('auth:registration_blocked')

    def is_command_allowed(self):
        return services.registration.is_registration_open()

    def get_command_kwargs(self):
        return {
            'site': get_current_site(self.request),
            'request_scheme': get_request_scheme(self.request),
            'user_registered': BoundSignal(signals.user_registered, self),
        }


class ActivateUserView(CommandGetView):

    login_required = False
    template_name = 'users/activation_failed.j2'
    success_url = 'users:dashboard'

    def command(self):
        return services.activation.activate(
            activation_token='fake_activation_token',
            user_activated=BoundSignal(signals.user_activated, self),
        )
