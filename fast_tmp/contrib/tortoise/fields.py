import warnings
from typing import Any

from tortoise import ConfigurationError
from tortoise.fields import Field

from fast_tmp.contrib.tortoise.validators import FilePathValidator, ImagePathValidator


class FileField(Field[str], str):  # type: ignore
    def __init__(self, max_length: int = 255, **kwargs: Any) -> None:
        """
        default file path: media/model_name/file_name/xxx.file
        """
        super(FileField, self).__init__()
        if int(max_length) < 1:
            raise ConfigurationError("'max_length' must be >= 1")
        self.max_length = int(max_length)
        super().__init__(**kwargs)
        self.validators.append(FilePathValidator(self.max_length))

    def to_python_value(self, value: Any) -> Any:
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)  # pylint: disable=E1102
        self.validate(value)
        return value


class ImageField(Field[str], str):  # type: ignore
    def __init__(self, **kwargs: Any) -> None:
        """
        default file path: media/model_name/file_name/xxx.image
        """
        super(ImageField, self).__init__()
        self.max_length = 255
        super().__init__(**kwargs)
        self.validators.append(FilePathValidator(self.max_length))
        self.validators.append(ImagePathValidator())


class RichTextField(Field[str], str):  # type: ignore
    indexable = False
    SQL_TYPE = "TEXT"

    def __init__(
        self, pk: bool = False, unique: bool = False, index: bool = False, **kwargs: Any
    ) -> None:
        if pk:
            warnings.warn(
                "RichTextField as a PrimaryKey is Deprecated, use CharField instead",
                DeprecationWarning,
                stacklevel=2,
            )
        if unique:
            raise ConfigurationError(
                "RichTextField doesn't support unique indexes, consider CharField or another strategy"
            )
        if index:
            raise ConfigurationError("RichTextField can't be indexed, consider CharField")

        super().__init__(pk=pk, **kwargs)

    class _db_mysql:
        SQL_TYPE = "LONGTEXT"

    class _db_mssql:
        SQL_TYPE = "NVARCHAR(MAX)"

    class _db_oracle:
        SQL_TYPE = "NCLOB"
