# -*- coding: utf-8 -*-
from unittest import mock

from django.urls import reverse
from django_webtest import WebTest


class IndexTest(WebTest):

    def test(self):
        self.renew_app()
        response = self.app.get(reverse('index'))
        assert response.status_int == 200
        assert '<h1>Welcome!</h1>' in response


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
        assert response.status_int == 200
        form = response.form
        form.lint()
        assert tuple(form.fields.keys()) == (
            'csrfmiddlewaretoken',
            'username',
            'real_password_field',
            'password',
            'log_in',
        )
