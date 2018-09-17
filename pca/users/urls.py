# -*- coding: utf-8 -*-
from django.urls.conf import path
from django.views.generic.base import TemplateView

app_name = 'users'
urlpatterns = [
    path('dashboard', TemplateView.as_view(template_name='users/dashboard.j2'), name='dashboard'),
]
