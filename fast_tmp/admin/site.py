from typing import Any, Dict

from requests import Request
from tortoise import Model

from fast_tmp.models import Group, Permission, User
from fast_tmp.site import ModelAdmin
from fast_tmp.site.field import Password


class UserAdmin(ModelAdmin):
    model = User
    list_display = ("name", "username", "is_active", "is_superuser", "is_staff")
    inline = ("is_active", "is_superuser", "is_staff")
    create_fields = (
        "username",
        "password",
        "name",
        "groups",
        "permissions",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    update_fields = (
        "username",
        "password",
        "name",
        "groups",
        "permissions",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    fields = {"password": Password}


class GroupAdmin(ModelAdmin):
    model = Group
    list_display = ("name", "users", "permissions")
    create_fields = ("name", "users", "permissions")
    update_fields = ("name", "users", "permissions")


class PermissionAdmin(ModelAdmin):
    model = Permission
    list_display = ("label", "codename", "users", "groups")
    create_fields = ("label", "codename", "users", "groups")
    update_fields = ("label", "codename", "users", "groups")
