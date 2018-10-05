# -*- coding: utf-8 -*-
import pytest
from django_webtest import DjangoTestApp


@pytest.fixture()
def app():
    return DjangoTestApp()


@pytest.fixture(scope='session', autouse=True)
def django_webtest_pdb_shim():
    from django_webtest import WebTestMixin

    def debug(self):
        self.renew_app()
        super(WebTestMixin, self).debug()

    WebTestMixin.debug = debug
