from test_example.models import FieldTesting

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
    )
    create_fields = (
        "name",
        "age",
        "desc",
        "married",
        "degree",
        "degree_inline",
        "gender",
        "created_time",
        "birthday",
        "config",
        "max_time_length",
    )
