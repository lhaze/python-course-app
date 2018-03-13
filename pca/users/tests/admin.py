# -*- coding: utf-8 -*-
import pytest

from pca.utils.tests import get_error_codes

from ..admin import (
    # AdminUserChangeForm,
    AdminUserCreationForm,
)


@pytest.mark.django_db
class TestAdminUserCreationForm:
    data = {
        'email': 'some_user@pca.org',
        'name': 'some_user',
        'password1': 'some1password!',
        'password2': 'some1password!',
    }

    def test_success(self):
        form = AdminUserCreationForm(self.data)
        assert form.is_valid()
        user = form.save(commit=False)
        assert user.email == self.data['email']
        assert user._password == self.data['password1']

    def test_password_mismatch(self):
        data = dict(self.data, password2='password2')
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_mismatch']}

    def test_password_too_similar(self):
        data = dict(
            self.data,
            password1='user@pca.org',
            password2='user@pca.org',
        )
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_similar']}

    def test_password_too_short(self):
        data = dict(
            self.data,
            password1='asdzxc',
            password2='asdzxc',
        )
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_short']}

    def test_password_too_common(self):
        data = dict(
            self.data,
            password1='password',
            password2='password',
        )
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_common']}

    def test_password_numerics_only(self):
        data = dict(
            self.data,
            password1='18273645',
            password2='18273645',
        )
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_entirely_numeric']}

    def test_email_blacklist(self):
        data = dict(self.data, email='some_guy@10mail.org')
        form = AdminUserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'email': ['blacklist']}

    def test_display_name_no_blacklist(self):
        data = dict(self.data, display_name='admin')
        form = AdminUserCreationForm(data)
        assert form.is_valid()