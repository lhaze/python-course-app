# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)

from .models import User


class UserCreationForm(BaseUserCreationForm):

    class Meta:
        model = User
        fields = ('email',)


class UserChangeForm(BaseUserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_superuser', 'is_staff', 'date_joined')
    list_filter = ('is_superuser', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
    search_fields = ('email',)
    ordering = ('email', 'date_joined')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
