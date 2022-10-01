from fast_tmp.site import ModelAdmin

from .testmodels import Author, Book, Role


class RoleModel(ModelAdmin):
    model = Role
    list_display = (
        "name",
        "age",
        "married",
        "degree",
        "create_time",
        "birthday",
        "config",
        "max_time_length",
    )
    create_fields = (
        "name",
        "age",
        "desc",
        "married",
        "degree",
        "gender",
        "create_time",
        "birthday",
        "config",
        "max_time_length",
    )
    update_fields = (
        "name",
        "age",
        "desc",
        "married",
        "degree",
        "gender",
        "create_time",
        "birthday",
        "config",
        "max_time_length",
    )


class BookModel(ModelAdmin):
    model = Book
    list_display = ("name", "author", "rating")
    create_fields = ("name", "author", "rating")
    update_fields = ("name", "author")
    filters = ("name__contains",)


class AuthorModel(ModelAdmin):
    model = Author
    list_display = ("name",)
    create_fields = ("name",)
    inline = ("name",)
    update_fields = ("name",)
