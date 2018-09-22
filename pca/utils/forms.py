# -*- coding: utf-8 -*-
import abc

from business_logic import LogicException
from crispy_forms.helper import FormHelper
from django.forms import Form, ModelForm


class CrispyHelper(FormHelper):

    def __init__(self, form, **kwargs):
        """Push constructor kwargs into the __dict__"""
        super().__init__(form=form)
        self.__dict__.update(kwargs)


class CommandFormMixin(metaclass=abc.ABCMeta):

    command_result = None
    error_map = None

    @abc.abstractmethod
    def command(self):
        """Hook for a command call"""

    def map_error(self, error):
        error_code = error.error_code
        mapped_field = self.error_map and self.error_map.get(error_code)
        if not mapped_field:
            return False
        if mapped_field not in self.fields:
            return False
        self.add_error(mapped_field, error.message)
        return True

    def _post_clean(self):
        super()._post_clean()
        try:
            self.command_result = self.command()
        except LogicException as e:
            is_mapped = self.map_error(e)
            if not is_mapped:
                raise


class CommandForm(CommandFormMixin, Form):
    pass


class CommandModelForm(CommandFormMixin, ModelForm):
    pass
