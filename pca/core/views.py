# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .errors import ActionError


class ActionViewMixin:

    disallowed_url = None
    login_required = True
    raise_permission_exception = False
    permission_denied_message = ''
    redirect_field_name = REDIRECT_FIELD_NAME
    result = None

    def is_action_allowed(self):
        return True

    def has_permission(self):
        return not self.login_required or self.request.user.is_authenticated

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self):
        if self.raise_permission_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=settings.LOGIN_URL,
            redirect_field_name=self.get_redirect_field_name()
        )

    def dispatch(self, *args, **kwargs):
        if not self.is_action_allowed():
            return HttpResponseRedirect(force_text(self.disallowed_url))
        elif not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(*args, **kwargs)

    def action(self, *args, **kwargs):
        raise NotImplementedError


class ActionView(ActionViewMixin, FormView):

    def action(self, form, *args, **kwargs):
        raise NotImplementedError

    def form_valid(self, form):
        try:
            self.result = self.action(form)
        except ActionError:
            return self.form_invalid(form)


class ActionGetView(ActionViewMixin, TemplateView):

    success_url = None

    def action(self):
        raise NotImplementedError

    def get_success_url(self):
        return force_text(self.success_url)

    def get(self, request, *args, **kwargs):
        extra_context = {}
        try:
            self.result = self.action()
        except ActionError as e:
            extra_context['activation_error'] = {
                'message': e.message,
                'code': e.code,
                'params': e.params
            }
        else:
            return HttpResponseRedirect(force_text(self.get_success_url()))
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)
