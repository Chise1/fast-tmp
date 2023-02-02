from test_example.models import Author, Book, FieldTesting

from fast_tmp.site import ModelAdmin


class FieldTestingModel(ModelAdmin):
    model = FieldTesting
    list_display = (
        "name",
        "age",
        "name_inline",
        "age_inline",
        "married",
        "married_inline",
        "degree",
        "degree_inline",
        "created_time",
        "birthday",
        "config",
        "max_time_length",
        "def_time",
        "def_time2",
    )
    inline = (
        "name_inline",
        "age_inline",
        "married",
        "married_inline",
        "degree_inline",
        "birthday",
        "config",
        "max_time_length",
        "def_time",
        "def_time2",
    )
    create_fields = (
        "name",
        "age",
        "desc",
        "married",
        "married_inline",
        "degree",
        "degree_inline",
        "gender",
        "created_time",
        "birthday",
        "config",
        "max_time_length",
        "def_time",
        "def_time2",
    )
    update_fields = create_fields


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
    filters = ["birthday", "birthday__gte", "birthday__lte"]
