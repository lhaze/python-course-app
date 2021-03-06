# -*- coding: utf-8 -*-
from django.contrib.auth import models as auth_models
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import EmailDomainBlacklistValidator


class UserManager(auth_models.BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):

    USERNAME_FIELD = 'email'
    NAME_MAX_LEN = 32
    EMAIL_VALIDATORS = [
        EmailValidator(),
        EmailDomainBlacklistValidator(),
    ]

    email = models.EmailField(
        _('email address'),
        validators=EMAIL_VALIDATORS,
        unique=True
    )
    name = models.CharField(
        _('displayed name'),
        max_length=NAME_MAX_LEN,
        unique=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()
