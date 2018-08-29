# -*- coding: utf-8 -*-
import unicodedata

from django import forms
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    forms as auth_forms,
)
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from xxhash import xxh64

from .services import mark_session_unauthorized
from .validators import NameBlacklistValidator, NameUnicodeValidator

User = get_user_model()


class NameField(forms.CharField):
    def to_python(self, value):
        value = super().to_python(value).lower()
        return unicodedata.normalize('NFKC', value)


class UserCreationForm(auth_forms.UserCreationForm):

    NAME_MIN_LEN = 5
    NAME_MAX_LEN = User.NAME_MAX_LEN
    NAME_VALIDATORS = [
        NameBlacklistValidator(),
        NameUnicodeValidator(),
    ]

    name = NameField(
        help_text=_("Displayed user name."),
        min_length=NAME_MIN_LEN,
        max_length=NAME_MAX_LEN,
        validators=NAME_VALIDATORS
    )

    class Meta:
        model = User
        fields = ('email',)


class AuthenticationForm(auth_forms.AuthenticationForm):
    """
    Authentication form with honeypot password field.
    """
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
        self.fields[self._get_password_field_key] = forms.CharField(
            label=_("Password"),
            strip=False,
            widget=forms.PasswordInput,
        )

    @cached_property
    def _get_password_field_key(self):
        """Get hash from session_key"""
        if not self.request.session.session_key:
            # force creation of session when session isn't already created
            self.request.session.save()
        hash = xxh64(self.request.session.session_key, seed=settings.NON_SECRET_KEY).hexdigest()
        return "f{}".format(hash)

    def clean(self):
        import pdb; pdb.set_trace()
        username = self.cleaned_data.get('username')
        real_password = self.cleaned_data.get(self._get_password_field_key)
        fake_password = self.cleaned_data.get('password')

        if fake_password is not None:
            self.fake_password_provided(username, fake_password, real_password)
        elif username is not None and real_password:
            self.user_cache = authenticate(self.request, username=username, password=real_password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def fake_password_provided(self, username, fake_password, real_password):
        """Do sth about unauthorized login attempt"""
        self.unauthorized_attempt = True
        mark_session_unauthorized(self.request, username, fake_password, real_password)
