# -*- coding: utf-8 -*-
from django.http import HttpRequest


def get_request_scheme(request: HttpRequest) -> str:
    return 'https' if request.is_secure() else 'http'
