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
            'password',
            'real_password_field',
            'log_in',
        )


'''
<form>
<input name="csrfmiddlewaretoken" type="hidden"
value="DC77bUK4IxZLoWJYrvpqSADJoYwlNVDpBu9OIUHMbULggRvDqjVufgmq53bspkCX"/>
<div class="form-group">
<label for="id_username">Email</label>
<input autofocus="" id="id_username" maxlength="254" name="username" required="" type="text"/>
</div>
<div class="form-group">
<label for="id_password">Password</label>
<input id="id_password" name="password" type="password"/>
</div>
<input class="btn btn btn-primary" type="submit" value="Log In"/>
<a class="pull-right" href="#">Forgot password?</a>
</form>
'''
