# -*- coding: utf-8 -*-
import typing as t

from business_logic import LogicException
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm


class CrispyHelper(FormHelper):

    def __init__(self, form, **kwargs):
        """Push constructor kwargs into the __dict__"""
        super().__init__(form=form)
        self.__dict__.update(kwargs)


class CommandFormMixin():

    result = None
    error_map: t.Mapping[str, t.List[str]] = None

    def __init__(self, *args, command_kwargs=None, **kwargs):
        self.command_kwargs = command_kwargs or {}
        super().__init__(*args, **kwargs)

    def command(self, **kwargs):
        """
        Hook for a command call. Here you can use values of the form from
        self.cleaned_data attribute and custom kwargs from self.command_kwargs
        attribute.
        """
        raise NotImplementedError

    def map_error(self, error: LogicException):
        mapped_field = self.error_map and self.error_map.get(error.error_code)
        mapped_error = ValidationError(error.args[0], error.error_code)
        self.add_error(mapped_field, mapped_error)

    def _post_clean(self):
        super()._post_clean()
        try:
            self.result = self.command(**self.command_kwargs)
        except LogicException as e:
            self.map_error(e)


class CommandForm(CommandFormMixin, Form):
    pass


class CommandModelForm(CommandFormMixin, ModelForm):
    pass
