# -*- coding: utf-8 -*-
from django.conf import settings as django_settings


def settings(request):
    """
    Adds the settings specified in settings.TEMPLATE_VISIBLE_SETTINGS to
    the request context.
    """
    return {
        attr: getattr(django_settings, attr, 'UNDEFINED')
        for attr in getattr(django_settings, "TEMPLATE_VISIBLE_SETTINGS", ())
    }
