from fast_tmp.admin.schema.abstract_schema import BaseAmisModel


class Json(BaseAmisModel):
    type = "json"
    source: str
