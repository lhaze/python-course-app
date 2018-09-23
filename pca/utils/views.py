# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views.generic.edit import FormView

from business_logic import LogicException

from . import forms


class PermissionMixin:

    request = None
    disallowed_url = None
    login_required = True
    permission_denied_message = ''
    redirect_field_name = REDIRECT_FIELD_NAME
    result = None

    def is_operation_allowed(self):
        return True

    def has_permission(self):
        return not self.login_required or self.request.user.is_authenticated

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def handle_command_disallowed(self):
        return HttpResponseRedirect(force_text(self.disallowed_url))

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                next=self.request.get_full_path(),
                login_url=settings.LOGIN_URL,
                redirect_field_name=self.redirect_field_name
            )
        raise PermissionDenied(self.get_permission_denied_message())

    def dispatch(self, *args, **kwargs):
        if not self.is_operation_allowed():
            return self.handle_command_disallowed()
        elif not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(*args, **kwargs)


class CommandView(PermissionMixin, FormView):

    def get_command_kwargs(self):
        return {}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return dict(kwargs, command_kwargs=self.get_command_kwargs())

    def form_valid(self, form: forms.CommandFormMixin):
        self.result = form.result
        super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['result'] = self.result
        return data


class CommandGetView(CommandView):

    success_url = None

    def command(self):
        raise NotImplementedError

    def get_success_url(self):
        return force_text(self.success_url)

    def get(self, request, *args, **kwargs):
        extra_context = {}
        try:
            self.result = self.command()
        except LogicException as e:
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
