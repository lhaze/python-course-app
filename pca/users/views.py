from django.contrib.auth import views as auth_views
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from django.views import generic as generic_views

from . import forms


class LoginView(auth_views.LoginView):
    form_class = forms.AuthenticateForm
    template_name = 'users/login.j2'


class RegisterView(generic_views.CreateView):
    form_class = forms.UserCreateForm
    template_name = 'users/register.j2'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, ValidationError(
                _('An error occurred. Please, try again.'), code='constraints'
            ))
            return self.form_invalid(form)
