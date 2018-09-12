# -*- coding: utf-8 -*-
import unicodedata

from crispy_forms.layout import Div, Layout
from django import forms
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    forms as auth_forms,
)
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_registration import validators as django_registration_validators
from xxhash import xxh64

from pca.utils.forms import CrispyHelper
from .services import mark_login_suspicious
from .validators import (
    EmailDomainBlacklistValidator,
    NameBlacklistValidator,
    NameUnicodeValidator,
)

User = get_user_model()


class NameField(forms.CharField):
    def to_python(self, value):
        value = super().to_python(value).lower()
        return unicodedata.normalize('NFKC', value)


class UserCreateForm(auth_forms.UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

    NAME_MIN_LEN = 5
    NAME_MAX_LEN = User.NAME_MAX_LEN
    NAME_VALIDATORS = [
        NameBlacklistValidator(),
        NameUnicodeValidator(),
        django_registration_validators.CaseInsensitiveUnique(
            User, 'name', _('This name is already taken. Please choose another.')),
    ]
    EMAIL_VALIDATORS = [
        django_registration_validators.CaseInsensitiveUnique(
            User, 'email', _('This email is already registered. Please choose another.')),
        django_registration_validators.validate_confusables_email,
        EmailDomainBlacklistValidator(),
    ]

    name = NameField(
        help_text=_("Displayed user name."),
        min_length=NAME_MIN_LEN,
        max_length=NAME_MAX_LEN,
        validators=NAME_VALIDATORS
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CrispyHelper(
            self,
            field_class="textinput textInput",
            form_tag=False,
        )
        self.fields['email'].validators.extend(self.EMAIL_VALIDATORS)


class AuthenticateForm(auth_forms.AuthenticationForm):
    """
    Authentication form with honeypot password field.
    """
    user = None
    password = forms.CharField(
        label=_("Password"),
        required=False,
        strip=False,
        widget=forms.PasswordInput,
    )
    unauthorized_attempt = False

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        super().__init__(request, *args, **kwargs)
        self.fields[self._password_field_key] = forms.CharField(
            label=_("Password"),
            strip=False,
            widget=forms.PasswordInput,
        )
        self.helper = CrispyHelper(
            self,
            field_class="textinput textInput",
            form_tag=False,
            layout=Layout(
                'username',
                self._password_field_key,
                Div(
                    'password',
                    style='display: none'
                ),
            )
        )

    @cached_property
    def _password_field_key(self):
        """Get hash from session_key"""
        if not self.request.session.session_key:
            # force creation of session when session isn't already created
            self.request.session.save()
        hash_ = xxh64(self.request.session.session_key, seed=settings.NON_SECRET_KEY).hexdigest()
        return "f{}".format(hash_)

    def clean(self):
        username = self.cleaned_data.get('username')
        real_password = self.cleaned_data.get(self._password_field_key)
        fake_password = self.cleaned_data.get('password')

        if fake_password:
            self.fake_password_provided(username, fake_password, real_password)
        elif username is not None and real_password:
            self.user = authenticate(self.request, username=username, password=real_password)
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user)

        return self.cleaned_data

    def fake_password_provided(self, username, fake_password, real_password):
        """Do sth about unauthorized login attempt"""
        self.unauthorized_attempt = True
        mark_login_suspicious(self.request, username, fake_password, real_password)
