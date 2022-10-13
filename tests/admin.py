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
    list_display = ("name", "author", "rating", "cover")
    create_fields = ("name", "author", "rating", "cover")
    update_fields = ("name", "author", "cover")
    filters = ("name__contains",)


class AuthorModel(ModelAdmin):
    model = Author
    list_display = ("name", "birthday")
    create_fields = ("name", "birthday")
    inline = ("name",)
    update_fields = ("name", "birthday")
