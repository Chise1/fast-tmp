from fast_tmp.site import ModelAdmin
from .models import UserInfo


class UserInfoAdmin(ModelAdmin):
    model = UserInfo
    create_fields = [UserInfo.name, UserInfo.age, UserInfo.birthday, UserInfo.money, UserInfo.height, UserInfo.info,
                    UserInfo.tag, UserInfo.is_superuser]
    update_fields = create_fields
    list_display =  [UserInfo.id,UserInfo.name, UserInfo.age, UserInfo.birthday, UserInfo.money, UserInfo.height, UserInfo.info,
                    UserInfo.tag, UserInfo.is_superuser]