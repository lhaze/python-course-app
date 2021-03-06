# -*- coding: utf-8 -*-
import pytest
from unittest import mock

from pca.utils.tests import get_error_codes

from ..forms import (
    AuthenticateForm,
    UserCreateForm,
)


USER_NAME_BLACKLIST = ('admin', 'webmaster')


@pytest.mark.django_db
class TestUserCreateForm:

    data = {
        'email': 'some_user@pca.org',
        'name': 'some_user',
        'password1': 'some1password!',
        'password2': 'some1password!',
    }

    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.USER_NAME_BLACKLIST = 'pca.users.tests.forms.USER_NAME_BLACKLIST'
        return settings

    @pytest.fixture
    def command_kwargs(self, site):
        return {
            'site': site,
            'request_scheme': 'https',
            'user_registered': mock.MagicMock()
        }

    def test_success(self, command_kwargs):
        form = UserCreateForm(self.data, command_kwargs=command_kwargs)
        assert form.is_valid()
        user = form.save(commit=False)
        assert user.email == self.data['email']
        assert user._password == self.data['password1']

    def test_username_mixed_case(self, command_kwargs):
        data = {**self.data, 'name': 'SomE UsEr'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert form.is_valid()
        assert form.cleaned_data['name'] == 'some user'

    def test_name_blacklist(self, command_kwargs):
        data = {**self.data, 'name': 'admin'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'name': ['blacklist']}

    def test_name_too_short(self, command_kwargs):
        data = {**self.data, 'name': 'adm'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'name': ['min_length']}

    def test_name_with_homoglyph(self, command_kwargs):
        """Name has a confusable homoglyph -- it should be error"""
        data = {**self.data, 'name': 'Alloρ'}  # greek ro which might be confusing with latin p
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'name': ['mixed_unicode']}

    def test_password_mismatch(self, command_kwargs):
        data = {**self.data, 'password2': 'password2'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_mismatch']}

    def test_password_too_similar(self, command_kwargs):
        data = {**self.data, 'password1': 'user@pca.org', 'password2': 'user@pca.org'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_similar']}

    def test_password_too_short(self, command_kwargs):
        data = {**self.data, 'password1': 'asdzxc', 'password2': 'asdzxc'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_short']}

    def test_password_too_common(self, command_kwargs):
        data = {**self.data, 'password1': 'password', 'password2': 'password'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_too_common']}

    def test_password_numerics_only(self, command_kwargs):
        data = {**self.data, 'password1': '18273645', 'password2': '18273645'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'password2': ['password_entirely_numeric']}

    def test_email_blacklist(self, command_kwargs):
        data = {**self.data, 'email': 'some_guy@10mail.org'}
        form = UserCreateForm(data, command_kwargs=command_kwargs)
        assert not form.is_valid()
        assert get_error_codes(form) == {'email': ['blacklist']}


@pytest.mark.django_db
class TestAuthenticateForm:

    session_key = 'my_session_key'
    password_field = 'f81504bad8fe7a1eb'
    data = {
        'username': 'some_user@pca.org',
        password_field: 'my_password'
    }

    @pytest.fixture
    def user(self):
        from ..models import User
        return User(email=self.data['username'], is_active=True)

    @pytest.fixture(autouse=True)
    def authenticate(self, user):
        with mock.patch('pca.users.forms.authenticate') as mocked_authenticate:
            mocked_authenticate.return_value = user
            yield mocked_authenticate

    @pytest.fixture
    def mark_suspicious(self):
        with mock.patch('pca.users.services.login.mark_login_suspicious') \
                as mocked_mark_suspicious:
            yield mocked_mark_suspicious

    @pytest.fixture
    def req(self):
        request = mock.MagicMock()
        request.session.session_key = self.session_key
        return request

    def test_valid_attempt(self, req, mark_suspicious):
        """form.data is ok -- everything is fine"""
        form = AuthenticateForm(req, self.data)
        assert form.is_valid()
        assert not form.is_attempt_suspicious
        mark_suspicious.assert_not_called()

    def test_unauthorized_attempt(self, req, mark_suspicious):
        """Honeypot field `password` got a value -- be valid but do sth about that"""
        data = {**self.data, 'password': 'fake_password'}
        form = AuthenticateForm(req, data)
        assert form.is_valid()
        assert form.is_attempt_suspicious
        mark_suspicious.assert_called_once_with(
            req, data['username'], data['password'], data[self.password_field])

    def test_invalid_attempt(self, req, authenticate, mark_suspicious):
        """Honeypot is not filled, but credentials are invalid"""
        authenticate.return_value = None
        form = AuthenticateForm(req, self.data)
        assert not form.is_valid()
        assert not form.is_attempt_suspicious
        mark_suspicious.assert_not_called()
        assert get_error_codes(form) == {'__all__': ['invalid_login']}

    def test_inactive(self, req, user, mark_suspicious):
        """Credentials are ok and the user is inactive"""
        user.is_active = False
        form = AuthenticateForm(req, self.data)
        assert not form.is_valid()
        assert not form.is_attempt_suspicious
        mark_suspicious.assert_not_called()
        assert get_error_codes(form) == {'__all__': ['inactive']}
