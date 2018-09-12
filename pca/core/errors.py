# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError


class ActionError(ValidationError):
    pass
