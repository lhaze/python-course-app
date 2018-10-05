# -*- coding: utf-8 -*-
import pytest
from unittest import mock

from pca.main.factories import SiteFactory


@pytest.fixture(scope='session', autouse=True)
def domain():
    return 'testserver'


@pytest.fixture(autouse=True)
def site(domain, db):
    site = SiteFactory(name=domain, domain=domain)
    with mock.patch('django.contrib.sites.shortcuts.get_current_site') as mocked_get_current_site:
        mocked_get_current_site.return_value = site
        yield site
