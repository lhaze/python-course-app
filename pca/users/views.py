from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from pca.core.views import ActionView, ActionGetView
from . import forms, services


class LoginView(auth_views.LoginView):
    form_class = forms.AuthenticateForm
    template_name = 'users/login.j2'


class RegisterView(ActionView):

    login_required = False
    form_class = forms.UserCreateForm
    template_name = 'users/register.j2'
    success_url = settings.LOGIN_REDIRECT_URL
    disallowed_url = reverse_lazy('auth:registration_blocked')

    def is_action_allowed(self):
        return services.is_registration_allowed()

    def action(self, form, *args, **kwargs):
        try:
            return services.register(self.request, form)
        except IntegrityError:
            form.add_error(None, ValidationError(
                _('An error occurred. Please, try again.'), code='constraints'
            ))
            raise


class ActivateUserView(ActionGetView):

    login_required = False
    template_name = 'users/activation_failed.j2'
    success_url = 'users:me'

    def action(self):
        return services.activate(*self.args, **self.kwargs)
