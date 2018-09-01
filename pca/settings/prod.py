# -*- coding: utf-8 -*-
"""
Django settings for python_course_app project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import disposable_email_domains
import django_heroku
import dotenv

from pca.utils.config import env_var, path, trueish, env_json_var


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path(__file__, '..', '..', '..')
dotenv.read_dotenv(path(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# this should be changed by django-heroku or dotenv auto-configured
SECRET_KEY = env_var('SECRET_KEY', '333w=r#mhn$r6n_#-*6#p2rd#!_0ly0=*vd=x1@((i+04@0=31')
# Not so secret key (the real secret should be kept only for da real secrets like
# generation of the session keys)
NON_SECRET_KEY = int(env_var('NON_SECRET_KEY', '20141025'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = trueish(env_var('DJANGO_DEBUG', False))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'django_extensions',

    'pca.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'OPTIONS': {'user_attributes': ('email', 'display_name')},
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {'min_length': 8},
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}]
LOGIN_REDIRECT_URL = 'users:me'


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [path(BASE_DIR, "static")]

LOGGING = {}

# Configure Django App for Heroku.
django_heroku.settings(locals())

LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'pca': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    '': {
        'handlers': ['console'],
        'level': 'ERROR',
    }
}
LOGGING['formatters']['verbose'] = {
    'format':
        '%(asctime)s.%(msecs)03d|%(process)d|%(levelname)s|%(pathname)s:%(lineno)s| %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}


# Custom webapp configuration
USER_EMAIL_DOMAIN_BLACKLIST = disposable_email_domains.blacklist
USER_NAME_BLACKLIST = set(env_json_var('USER_NAME_BLACKLIST', ()))
