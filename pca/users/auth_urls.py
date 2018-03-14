# -*- coding: utf-8 -*-
from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path('login', TemplateView.as_view(template_name='auth/login.html')),
]
