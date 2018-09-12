# -*- coding: utf-8 -*-
"""
Most of the services are extracted from views of django-registration==3.0 package.
"""
from django.contrib.auth import get_user_model
from django.core import signing
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from pca.core.errors import ActionError

from . import signals

User = get_user_model()


def mark_login_suspicious(request, username, fake_password, real_password):
    pass  # noop for now


def is_registration_allowed():
    return getattr(settings, 'REGISTRATION_OPEN', True)


def register(request, form):
    new_user = create_inactive_user(request, form)
    signals.user_registered.send(
        sender=form,
        user=new_user,
        request=request
    )
    return new_user


def create_inactive_user(request, form):
    """
    Create the inactive user account and send an email containing
    activation instructions.

    """
    new_user = form.save(commit=False)
    new_user.is_active = False
    new_user.save()
    send_activation_email(request, new_user)
    return new_user


_REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')
_EMAIL_SUBJECT_TEMPLATE = ''
_EMAIL_BODY_TEMPLATE = ''


def _get_activation_key(user):
    """Generate the activation key which will be emailed to the user."""
    return signing.dumps(
        obj=user.get_username(),
        salt=_REGISTRATION_SALT
    )


def _get_email_context(request, activation_key):
    """Build the template context used for the activation email."""
    scheme = 'https' if request.is_secure() else 'http'
    return {
        'scheme': scheme,
        'activation_key': activation_key,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'site': get_current_site(request)
    }


def send_activation_email(request, user):
    """
    Send the activation email. The activation key is the username,
    signed using TimestampSigner.

    """
    activation_key = _get_activation_key(user)
    context = _get_email_context(request, activation_key)
    context['user'] = user
    subject = render_to_string(
        template_name=_EMAIL_SUBJECT_TEMPLATE,
        context=context,
        request=request
    )
    # Force subject to a single line to avoid header-injection
    # issues.
    subject = ''.join(subject.splitlines())
    message = render_to_string(
        template_name=_EMAIL_BODY_TEMPLATE,
        context=context,
        request=request
    )
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


_ALREADY_ACTIVATED_MESSAGE = _(u"The account you tried to activate has already been activated.")
_BAD_USERNAME_MESSAGE = _(u"The account you attempted to activate is invalid.")
_EXPIRED_MESSAGE = _(u"This account has expired.")
_INVALID_KEY_MESSAGE = _(u"The activation key you provided is invalid.")


def activate(*args, **kwargs):
    username = _validate_activation_key(kwargs.get('activation_key'))
    user = _get_user(username)
    user.is_active = True
    user.save()
    return user


def _validate_activation_key(activation_key):
    """
    Verify that the activation key is valid and within the
    permitted activation time window, returning the username if
    valid or raising ``ActivationError`` if not.

    """
    try:
        username = signing.loads(
            activation_key,
            salt=_REGISTRATION_SALT,
            max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
        )
        return username
    except signing.SignatureExpired:
        raise ActionError(
            _EXPIRED_MESSAGE,
            code='expired'
        )
    except signing.BadSignature:
        raise ActionError(
            _INVALID_KEY_MESSAGE,
            code='invalid_key',
            params={'activation_key': activation_key}
        )


def _get_user(username):
    """
    Given the verified username, look up and return the
    corresponding user account if it exists, or raising
    ``ActivationError`` if it doesn't.

    """
    try:
        user = User.objects.get(**{
            User.USERNAME_FIELD: username,
        })
        if user.is_active:
            raise ActionError(
                _ALREADY_ACTIVATED_MESSAGE,
                code='already_activated'
            )
        return user
    except User.DoesNotExist:
        raise ActionError(
            _BAD_USERNAME_MESSAGE,
            code='bad_username'
        )
