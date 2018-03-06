# -*- coding: utf-8 -*-
from unittest.mock import sentinel


NO_ERROR_CODE = sentinel.NO_ERROR_CODE


def get_error_codes(form):
    return {
        name: [e.code or NO_ERROR_CODE for e in errors]
        for name, errors in form.errors.as_data().items()
    }
