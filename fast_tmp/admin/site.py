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
        "is_active",
        "is_superuser",
        "is_staff",
    )
    update_fields = (
        "username",
        "password",
        "name",
        "groups",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    fields = {"password": Password}  # type: ignore


class GroupAdmin(ModelAdmin):
    model = Group
    list_display = ("name", "users", "permissions")
    create_fields = ("name", "users", "permissions")
    update_fields = ("name", "users", "permissions")


# todo 增加同步权限的按钮
class PermissionAdmin(ModelAdmin):
    model = Permission
    list_display = ("label", "codename", "groups")
    create_fields = ("label", "codename", "groups")
    update_fields = ("label", "codename", "groups")
