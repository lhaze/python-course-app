# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper


class CrispyHelper(FormHelper):

    def __init__(self, form, **kwargs):
        """Push constructor kwargs into the __dict__"""
        super().__init__(form=form)
        self.__dict__.update(kwargs)
