# -*- coding: utf-8 -*-
from django.urls import reverse
from django_webtest import WebTest


class IndexTest(WebTest):

    def test_index(self):
        response = self.app.get(reverse('index'))
        assert response.status_int == 200
        assert response.html.find('title').text == 'PCA'
        assert '<h1>Welcome!</h1>' in response
