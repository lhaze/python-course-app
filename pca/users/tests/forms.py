# -*- coding: utf-8 -*-
import pytest

from pca.utils.tests import get_error_codes

from ..forms import UserCreationForm


@pytest.mark.django_db
class TestUserCreationForm:

    data = {
        'email': 'some_user@pca.org',
        'name': 'some_user',
        'password1': 'some1password!',
        'password2': 'some1password!',
    }

    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.USER_NAME_BLACKLIST = ('admin', 'webmaster')
        return settings

    def test_success(self):
        form = UserCreationForm(self.data)
        assert form.is_valid()
        user = form.save(commit=False)
        assert user.email == self.data['email']
        assert user._password == self.data['password1']

    def test_name_blacklist(self):
        data = dict(self.data, name='admin')
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'name': ['blacklist']}

    def test_name_too_short(self):
        data = dict(self.data, name='adm')
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'name': ['min_length']}

    def test_password_mismatch(self):
        data = dict(self.data, password2='password2')
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_mismatch']}

    def test_password_too_similar(self):
        data = dict(
            self.data,
            password1='user@pca.org',
            password2='user@pca.org',
        )
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_similar']}

    def test_password_too_short(self):
        data = dict(
            self.data,
            password1='asdzxc',
            password2='asdzxc',
        )
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_short']}

    def test_password_too_common(self):
        data = dict(
            self.data,
            password1='password',
            password2='password',
        )
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_common']}

    def test_password_numerics_only(self):
        data = dict(
            self.data,
            password1='18273645',
            password2='18273645',
        )
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_entirely_numeric']}

    def test_email_blacklist(self):
        data = dict(self.data, email='some_guy@10mail.org')
        form = UserCreationForm(data)
        assert not form.is_valid()
        assert get_error_codes(form) == {'email': ['blacklist']}
