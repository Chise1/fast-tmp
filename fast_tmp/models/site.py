from fast_tmp.models import User
from fast_tmp.site import ModelAdmin


class UserAdmin(ModelAdmin):
    model = User
    list_display = [User.id, User.username, User.is_active]
    create_fields = [User.username, User.password]
    update_fields = [User.password]