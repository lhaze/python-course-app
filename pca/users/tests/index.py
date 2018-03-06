# -*- coding: utf-8 -*-


def test_index(django_app):
    response = django_app.get('/')
    assert response.html.find('title').text == 'PCA'
