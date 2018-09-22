from django.conf import settings
from django.contrib.auth import (
    login as auth_login,
    views as auth_views,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from pca.core.views import ActionView, ActionGetView
from pca.utils.request import get_request_scheme
from . import forms, services


class LoginView(auth_views.LoginView):
    form_class = forms.AuthenticateForm
    template_name = 'users/login.j2'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.user)
        return HttpResponseRedirect(self.get_success_url())


class RegisterView(ActionView):

    request = None
    login_required = False
    form_class = forms.UserCreateForm
    template_name = 'users/sign_up.j2'
    success_url = settings.LOGIN_REDIRECT_URL
    disallowed_url = reverse_lazy('auth:registration_blocked')

    def is_action_allowed(self):
        return services.registration.is_registration_opened()

    def action(self, form, *args, **kwargs):
        user = form.save(commit=False)
        site = get_current_site(self.request)
        request_scheme = get_request_scheme(self.request)
        try:
            return services.registration.register(user, site, request_scheme)
        except IntegrityError:
            form.add_error(None, ValidationError(
                _('An error occurred. Please, try again.'), code='constraints'
            ))
            raise


class ActivateUserView(ActionGetView):

    login_required = False
    template_name = 'users/activation_failed.j2'
    success_url = 'users:dashboard'

    def action(self):
        return services.activation.activate()
