# -*- coding: utf-8 -*-
from unittest import mock

from django.urls import reverse
from django_webtest import WebTest


class AuthTest(WebTest):
    # fixtures = ['users.json']

    def test_login_form(self):
        self.renew_app()
        with mock.patch(
            'pca.users.forms.AuthenticationForm._password_field_key',
            new_callable=mock.PropertyMock
        ) as password_field_key:
            password_field_key.return_value = 'real_password_field'
            response = self.app.get(reverse('auth:login'))
        form = response.form
        form.lint()
        assert tuple(form.fields.keys()) == (
            'csrfmiddlewaretoken',
            'username',
            'real_password_field',
            'password',
            'log_in',
        )
