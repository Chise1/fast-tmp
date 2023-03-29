from datetime import datetime, timedelta

from jose import jwt  # type: ignore

from fast_tmp.conf import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    now = datetime.now()
    expire = now + expires_delta
    to_encode.update({"exp": expire.timestamp(), "create_time": now.timestamp()})
    if not SECRET_KEY:
        raise AttributeError("SECRET_KEY can not be none")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(
    token: str,
):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
