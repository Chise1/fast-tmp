from typing import Any

from starlette.requests import Request
from tortoise import Model

from fast_tmp.amis.forms import Control, ControlEnum
from fast_tmp.contrib.auth.hashers import make_password
from fast_tmp.responses import TmpValueError
from fast_tmp.site.util import StrControl


# todo 以后考虑创建更新的control分离
class Password(StrControl):
    _control_type = ControlEnum.input_password
    _update_control = None

    async def get_value(self, request: Request, obj: Model) -> Any:
        return None

    async def set_value(self, request: Request, obj: Model, value: Any):
        if obj.pk is not None:
            old_password = getattr(obj, self.name)
            if value != old_password and len(value) > 0:
                setattr(obj, self.name, make_password(value))
        else:
            if not value:
                raise TmpValueError("password can not be none.")
            await super().set_value(request, obj, value)

    def get_control(self, request: Request) -> Control:
        if not self._control:
            self._control = Control(type=self._control_type, name=self.name, label=self.label)
            if not self._field.null:  # type: ignore
                if self._field.default is not None:  # type: ignore
                    self._control.value = self.orm_2_amis(self._field.default)  # type: ignore
        return self._control
