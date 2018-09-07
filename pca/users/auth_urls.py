# -*- coding: utf-8 -*-
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = 'auth'
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('register', views.RegisterView.as_view(), name='register'),
]
