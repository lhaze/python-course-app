# -*- coding: utf-8 -*-
from confusable_homoglyphs import confusables
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from business_logic import (
    LogicErrors,
    LogicException,
    validated_by,
    validator,
)

from .activation import send_activation_email
from .. import signals


class RegistrationErrors(LogicErrors):
    REGISTRATION_CLOSED = LogicException(
        _("Signup process is closed. Email us if you want to sign up anyway."),
        error_code='registration_closed'
    )
    CONFUSABLE_NAME = LogicException(
        _("This name cannot be registered. Please choose a different name."),
        error_code='confusable_name'
    )
    CONFUSABLE_EMAIL = LogicException(
        _("This email address cannot be registered. Please supply a different email address."),
        error_code='confusable_email'
    )


@validator
def is_registration_open():
    if not getattr(settings, 'REGISTRATION_OPEN', True):
        raise RegistrationErrors.REGISTRATION_CLOSED


@validator
def is_non_confusable_name(value):
    """
    Validator which disallows 'dangerous' values likely to
    represent homograph attacks.

    A username is 'dangerous' if it is mixed-script (as defined by
    Unicode 'Script' property) and contains one or more characters
    appearing in the Unicode Visually Confusable Characters file.

    """
    if confusables.is_dangerous(value, preferred_aliases=['latin']):
        raise RegistrationErrors.CONFUSABLE_NAME


@validator
def is_non_confusable_email(value):
    """
    Validator which disallows 'dangerous' email addresses likely to
    represent homograph attacks.

    An email address is 'dangerous' if either the local-part or the
    domain, considered on their own, are mixed-script and contain one
    or more characters appearing in the Unicode Visually Confusable
    Characters file.

    """
    if '@' not in value:
        return
    local_part, domain = value.split('@')
    if confusables.is_dangerous(local_part) or \
       confusables.is_dangerous(domain):
        raise RegistrationErrors.CONFUSABLE_EMAIL


@validator
def can_register(user, *args, **kwargs):
    return all((
        is_registration_open(),
        is_non_confusable_name(user.name),
        is_non_confusable_email(user.email)
    ))


@validated_by(can_register)
def register(user, site: Site, request_scheme: str):
    new_user = create_inactive_user(user, site, request_scheme)
    signals.user_registered.send(new_user)
    return new_user


def create_inactive_user(user, site, request_scheme):
    """
    Create the inactive user account and send an email containing
    activation instructions.
    """
    user.is_active = False
    user.save()
    send_activation_email(user, site, request_scheme)
    return user
