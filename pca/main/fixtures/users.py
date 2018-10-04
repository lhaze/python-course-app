# -*- coding: utf-8 -*-
import pytest

from pca.users.factories import UserFactory


@pytest.fixture(scope='session')
def admin_user():
    return UserFactory(name='admin', is_superuser=True)


@pytest.fixture(scope='session')
def staff_user():
    return UserFactory(name='staff', is_staff=True)


@pytest.fixture(scope='session')
def active_user():
    return UserFactory(name='active')


@pytest.fixture(scope='session')
def inactive_user():
    return UserFactory(name='inactive', email='foo@example.com')


@pytest.fixture(scope='session')
def users(admin_user, staff_user, active_user, inactive_user):
    return {
        'admin': admin_user,
        'staff': staff_user,
        'active': active_user,
        'inactive': inactive_user,
    }
