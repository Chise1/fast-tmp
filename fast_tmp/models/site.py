from typing import Any

from fast_tmp.models import User
from fast_tmp.site import ModelAdmin


class UserAdmin(ModelAdmin):
    model = User
    list_display = (User.id, User.username, User.is_active)
    create_fields = (User.username, User.password)
    update_fields = (User.password,)

    @classmethod
    def create_model(cls, data: dict) -> Any:
        user = cls.model(**data)
        user.set_password(user.password)
        return user

    @classmethod
    def update_model(cls, model: User, data: dict) -> Any:
        model.set_password(data["password"])
        return model
