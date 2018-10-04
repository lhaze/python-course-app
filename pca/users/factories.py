# -*- coding: utf-8 -*-
import datetime

import factory
from django.utils.dateparse import parse_datetime

from .models import User


STARTING_DATE = parse_datetime('2018-02-28 23:31:01.737228+00:00')


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = (User.USERNAME_FIELD,)

    name = factory.Sequence(lambda n: 'user_%d' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.name)
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True

    @factory.sequence
    def date_joined(n):
        return STARTING_DATE + datetime.timedelta(
            days=n, hours=n, minutes=n, seconds=n, milliseconds=n)

    @factory.sequence
    def last_login(n):
        n *= 2
        return STARTING_DATE + datetime.timedelta(
            days=n, hours=n, minutes=n, seconds=n, milliseconds=n)
