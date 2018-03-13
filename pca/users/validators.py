# -*- coding: utf-8 -*-
import abc

from confusable_homoglyphs import confusables
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
    message = _('Enter a valid email address.')

    @property
    def blacklist(self):
        return settings.USER_EMAIL_DOMAIN_BLACKLIST

    def get_validated_value(self, value):
        return value.rsplit('@', 1)[1]


class NameBlacklistValidator(BlacklistValidator):
    message = _('Enter a valid name.')

    @property
    def blacklist(self):
        return settings.USER_NAME_BLACKLIST

    def get_validated_value(self, value):
        return value


class NameUnicodeValidator:
    code = 'mixed_unicode'
    message = _('Enter a valid name.')

    def __call__(self, value):
        if bool(confusables.is_dangerous(value, preferred_aliases=['latin'])):
            raise ValidationError(self.message, code=self.code)
