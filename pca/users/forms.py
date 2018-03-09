# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from .models import User
from .validators import NameBlacklistValidator


class UserCreationForm(BaseUserCreationForm):

    NAME_MIN_LEN = 5
    NAME_MAX_LEN = User.NAME_MAX_LEN
    NAME_VALIDATORS = [NameBlacklistValidator()]

    name = fields.CharField(
        help_text=_(""),
        min_length=NAME_MIN_LEN,
        max_length=NAME_MAX_LEN,
        validators=NAME_VALIDATORS
    )

    class Meta:
        model = User
        fields = ('email',)
