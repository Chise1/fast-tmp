from tortoise import Model, fields


class Author(Model):
    name = fields.CharField(max_length=32)
