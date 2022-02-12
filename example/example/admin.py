from fast_tmp.site import ModelAdmin
from .models import UserInfo, Author, Book


class UserInfoAdmin(ModelAdmin):
    model = UserInfo
    create_fields = [UserInfo.name, UserInfo.age, UserInfo.birthday, UserInfo.money, UserInfo.height, UserInfo.info,
                     UserInfo.tag, UserInfo.is_superuser]
    update_fields = create_fields
    list_display = [UserInfo.id, UserInfo.name, UserInfo.age, UserInfo.birthday, UserInfo.money, UserInfo.height,
                    UserInfo.info,
                    UserInfo.tag, UserInfo.is_superuser]


class AuthorAdmin(ModelAdmin):
    model = Author
    create_fields = [Author.name, Author.books]
    list_display = create_fields


class BookAdmin(ModelAdmin):
    model = Book
    create_fields = [Book.name, Book.author]  # todo 增加提醒，可以为关系，可以为id
    list_display = [Book.id, Book.name, Book.author]  # todo 增加检查，必须在listplay里面带主键
    update_fields = create_fields
