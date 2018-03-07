# -*- coding: utf-8 -*-
import abc

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class BlacklistValidator:
    code = 'blacklist'

    @abc.abstractproperty
    def blacklist(self):
        pass

    @abc.abstractproperty
    def message(self):
        pass

    def __call__(self, value):
        validated_value = self.get_validated_value(value)
        if validated_value in self.blacklist:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            (self.blacklist == other.blacklist) and
            (self.message == other.message) and
            (self.code == other.code)
        )

    @abc.abstractmethod
    def get_validated_value(self, value):
        return value.rsplit('@', 1)[1]


class EmailBlacklistValidator(BlacklistValidator):
    blacklist = settings.USER_EMAIL_DOMAIN_BLACKLIST
    message = _('Enter a valid email address.')

    def get_validated_value(self, value):
        return value.rsplit('@', 1)[1]


class DisplayNameBlacklistValidator(BlacklistValidator):
    blacklist = settings.USER_DISPLAY_NAME_BLACKLIST
    message = _('Enter a valid display name.')

    def get_validated_value(self, value):
        return value
