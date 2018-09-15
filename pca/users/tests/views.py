# -*- coding: utf-8 -*-
from unittest import mock

from django.urls import reverse
from django_webtest import WebTest


class BaseMixin(WebTest):
    fixtures = ['example_users.yaml']
    real_password_field_name = 'real_password_field'


class LoginTest(BaseMixin, WebTest):

    def test_login_form(self):
        with mock.patch(
            'pca.users.forms.AuthenticateForm._password_field_key',
            new_callable=mock.PropertyMock
        ) as password_field_key:
            password_field_key.return_value = self.real_password_field_name
            response = self.app.get(reverse('auth:login'))
        assert response.status_int == 200
        form = response.form
        form.lint()
        assert tuple(form.fields.keys()) == (
            'csrfmiddlewaretoken',
            'username',
            self.real_password_field_name,
            'password',
            'log_in',
        )

    def test_login_success(self):
        with mock.patch(
            'pca.users.forms.AuthenticateForm._password_field_key',
            new_callable=mock.PropertyMock
        ) as password_field_key:
            password_field_key.return_value = self.real_password_field_name
            response = self.app.get(reverse('auth:login'))
            assert response.status_int == 200
            form = response.form
            form['username'] = 'ACTIVE@example.com'
            form[self.real_password_field_name] = 'active'
            response = form.submit()
            response.follow()


class RegisterTest(BaseMixin, WebTest):

    def test_register_form(self):
        response = self.app.get(reverse('auth:register'))
        assert response.status_int == 200
        form = response.form
        form.lint()
        assert tuple(form.fields.keys()) == (
            'csrfmiddlewaretoken',
            'email',
            'password1',
            'password2',
            'name',
            'submit'
        )
