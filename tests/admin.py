from fast_tmp.site import ModelAdmin, register_model_site

from .testmodels import Author, Book, Dec, IntEnumField, Role


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
        "money",
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
        "money",
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
        "money",
    )
    inline = update_fields


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


class DecModel(ModelAdmin):
    model = Dec
    list_display = ("dec1", "dec2")
    create_fields = list_display
    update_fields = list_display
    inline = list_display


class IntEnumAdmin(ModelAdmin):
    model = IntEnumField
    list_display = ("e1", "e2")
    create_fields = list_display
    update_fields = list_display
    inline = list_display


register_model_site({"fieldtesting": [IntEnumAdmin()]})
