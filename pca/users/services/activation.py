# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core import signing
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from business_logic import LogicErrors, LogicException

from pca.utils.config import get_setting

User = get_user_model()


_REGISTRATION_SALT = get_setting('REGISTRATION_SALT', 'registration')
_ACCOUNT_ACTIVATION_DAYS = get_setting('ACCOUNT_ACTIVATION_DAYS', 30)
_EMAIL_SUBJECT_TEMPLATE = ''
_EMAIL_BODY_TEMPLATE = ''
_DEFAULT_FROM_EMAIL = get_setting('GET_OWNER_EMAIL')


class ActivationErrors(LogicErrors):
    ALREADY_ACTIVATED = LogicException(
        _("The account you tried to activate has already been activated."))
    BAD_USERNAME = LogicException(_("The account you attempted to activate is invalid."))
    TOKEN_EXPIRED = LogicException(_("This account has expired."))
    INVALID_TOKEN = LogicException(_("The activation token you provided is invalid: {token}"))


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
        'expiration_days': _ACCOUNT_ACTIVATION_DAYS,
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
    user.email_user(subject, message, _DEFAULT_FROM_EMAIL)


def _get_activation_token(user):
    """Generate the activation key which will be emailed to the user."""
    return signing.dumps(
        obj=user.get_username(),
        salt=_REGISTRATION_SALT
    )


def activate(activation_token, user_activated):
    username = validate_activation_token(activation_token)
    user = get_user_to_activate(username)
    user.is_active = True
    user.save()
    user_activated.send(user)
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
            max_age=_ACCOUNT_ACTIVATION_DAYS * 86400
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
