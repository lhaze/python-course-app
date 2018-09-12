# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import forms as auth_forms
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AdminUserCreateForm(auth_forms.UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'name')


class AdminUserChangeForm(auth_forms.UserChangeForm):

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
class UserAdmin(auth_admin.UserAdmin):
    # The forms to add and change user instances
    form = AdminUserChangeForm
    add_form = AdminUserCreateForm

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
