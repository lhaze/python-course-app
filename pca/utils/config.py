# -*- coding: utf-8 -*-
import os


def path(*args):
    return os.path.abspath(os.path.join(*args))


def env_var(key, default=''):
    return os.environ.get(key, default)


def trueish(value):
    return bool(value) and str(value).lower() not in ['false', '0']
