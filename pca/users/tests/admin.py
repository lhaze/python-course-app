# -*- coding: utf-8 -*-
import pytest

from pca.utils.tests import get_error_codes

from ..admin import (
    # UserChangeForm,
    UserCreationForm,
)


@pytest.mark.django_db
class TestUserCreationForm:

    def test_success(self):
        data = {
            'email': 'user@pca.org',
            'password1': 'some1password!',
            'password2': 'some1password!',
        }
        form = UserCreationForm(data)
        assert form.is_valid()
        user = form.save(commit=False)
        assert user.email == data['email']
        assert user._password == data['password1']

    def test_password_mismatch(self):
        data = {
            'email': 'user@pca.org',
            'password1': 'password1',
            'password2': 'password2',
        }
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_mismatch']}

    def test_password_too_similar(self):
        data = {
            'email': 'user@pca.org',
            'password1': 'user@pca.org',
            'password2': 'user@pca.org',
        }
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_similar']}

    def test_password_too_short(self):
        data = {
            'email': 'user@pca.org',
            'password1': 'asdzxc',
            'password2': 'asdzxc',
        }
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_short']}

    def test_password_too_common(self):
        data = {
            'email': 'user@pca.org',
            'password1': 'password',
            'password2': 'password',
        }
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_common']}

    def test_password_numerics_only(self):
        data = {
            'email': 'user@pca.org',
            'password1': '18273645',
            'password2': '18273645',
        }
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_entirely_numeric']}
