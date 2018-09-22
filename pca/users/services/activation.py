# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core import signing
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from business_logic import LogicErrors, LogicException

from .. import signals

User = get_user_model()


_REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')
_EMAIL_SUBJECT_TEMPLATE = ''
_EMAIL_BODY_TEMPLATE = ''


class ActivationErrors(LogicErrors):
    ALREADY_ACTIVATED = LogicException(
        _("The account you tried to activate has already been activated."),
        error_code='already_activated')
    BAD_USERNAME = LogicException(
        _("The account you attempted to activate is invalid."), error_code='bad_username')
    TOKEN_EXPIRED = LogicException(
        _("This account has expired."), error_code='bad_username')
    INVALID_TOKEN = LogicException(
        _("The activation token you provided is invalid: {token}"), error_code='expired')


def send_activation_email(user, site, request_scheme):
    """
    Send the activation email. The activation key is the username,
    signed using TimestampSigner.

    """
    activation_token = _get_activation_token(user)
    context = {
        'user': user,
        'scheme': request_scheme,
        'activation_token': activation_token,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'site': site,
    }
    subject = render_to_string(
        template_name=_EMAIL_SUBJECT_TEMPLATE,
        context=context,
    )
    # Force subject to a single line to avoid header-injection
    # issues.
    subject = ''.join(subject.splitlines())
    message = render_to_string(
        template_name=_EMAIL_BODY_TEMPLATE,
        context=context,
    )
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


def _get_activation_token(user):
    """Generate the activation key which will be emailed to the user."""
    return signing.dumps(
        obj=user.get_username(),
        salt=_REGISTRATION_SALT
    )


def _get_email_context(activation_token, site):
    """Build the template context used for the activation email."""
    scheme = 'https' if request.is_secure() else 'http'
    return {
        'scheme': scheme,
        'activation_token': activation_token,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'site': site,
    }


def activate(activation_token):
    username = validate_activation_token(activation_token)
    user = get_user_to_activate(username)
    user.is_active = True
    user.save()
    signals.user_activated.send(user)
    return user


def validate_activation_token(activation_token):
    """
    Verify that the activation token is valid and within the
    permitted activation time window, returning the username if
    valid or raising ``ActivationError`` if not.
    """
    try:
        username = signing.loads(
            activation_token,
            salt=_REGISTRATION_SALT,
            max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
        )
        return username
    except signing.SignatureExpired:
        raise ActivationErrors.TOKEN_EXPIRED
    except signing.BadSignature:
        raise ActivationErrors.BAD_USERNAME


def get_user_to_activate(username):
    """
    Given the verified username, look up and return the corresponding user
    account if it exists, or raising one of ``ActivationErrors`` if it doesn't.
    """
    try:
        user = User.objects.get(**{User.USERNAME_FIELD: username})
        if user.is_active:
            raise ActivationErrors.ALREADY_ACTIVATED
        return user
    except User.DoesNotExist:
        raise ActivationErrors.BAD_USERNAME
