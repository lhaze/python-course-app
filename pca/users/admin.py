# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)
from django.utils.translation import gettext_lazy as _

from .models import User


class AdminUserCreationForm(BaseUserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'name')


class AdminUserChangeForm(BaseUserChangeForm):

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'password',
            'is_active',
            'is_superuser'
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'email',
        'name',
        'is_superuser',
        'is_staff',
        'date_joined'
    )
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'groups')
    search_fields = ('email', 'name')
    ordering = ('email', 'date_joined')
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('last_login',)
    fieldsets = (
        (_('User info'), {'fields': ('email', 'name', 'password')}),
        (_('Permissions'), {'fields': ('is_superuser', 'is_staff')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. (Base)UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
