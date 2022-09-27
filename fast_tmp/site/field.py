from typing import Any

from fast_tmp.contrib.auth.hashers import make_password
from fast_tmp.site.util import StrControl


class Password(StrControl):
    def amis_2_orm(self, value: Any) -> Any:
        return make_password(value)
