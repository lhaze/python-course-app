# -*- coding: utf-8 -*-
import json
import os


def path(*args):
    return os.path.abspath(os.path.join(*args))


def env_var(key, default=''):
    return os.environ.get(key, default)


def env_json_var(key, default=None):
    env_value = env_var(key)
    if not env_value:
        return default
    try:
        return json.loads(env_value)
    except json.JSONDecodeError:
        return default


def trueish(value):
    return bool(value) and str(value).lower() not in ['false', '0']
