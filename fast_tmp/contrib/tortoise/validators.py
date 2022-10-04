from os import path

from tortoise.exceptions import ValidationError
from tortoise.validators import Validator


class FilePathValidator(Validator):
    def __init__(self, max_length: int):
        self.max_length = max_length

    def __call__(self, value: str):
        if value is None:
            raise ValidationError("Value must not be None")
        if len(value) > self.max_length:
            raise ValidationError(f"Length of '{value}' {len(value)} > {self.max_length}")


class ImagePathValidator(Validator):
    def __call__(self, value: str):
        filename: str = path.splitext(value)[-1]
        if filename.lower() not in (".jpg", ".jpeg", ".png", ".gif"):
            raise ValidationError("File type must be image")
