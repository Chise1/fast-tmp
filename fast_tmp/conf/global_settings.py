from typing import Iterable

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_AUTH = True
EXPIRES_DELTA = 30
AUTH_USER_MODEL = "fast_tmp.User"

EXTRA_SCRIPT: Iterable[str] = []  # 额外的脚本指令地址
