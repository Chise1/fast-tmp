from fast_tmp.site import ModelAdmin
from test_example.models import FieldTesting


class FieldTestingModel(ModelAdmin):
    model = FieldTesting
    list_display = ("name", "age", "name_inline", "age_inline", "married", "married_inline")
    inline = ("name_inline", "age_inline", "married_inline")
