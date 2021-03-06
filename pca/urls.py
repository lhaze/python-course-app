# -*- coding: utf-8 -*-
"""python_course_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from pca.utils.config import env_var


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.j2'), name='index'),
    path('admin-{}/'.format(env_var('DJANGO_ADMIN_PATH', 'foo')), admin.site.urls),
    path('auth/', include('pca.users.auth_urls')),
    path('users/', include('pca.users.urls')),
]
