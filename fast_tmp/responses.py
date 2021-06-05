from fastapi import HTTPException
from starlette import status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
no_permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User has no permissions.",
)
amis_credentials_exception = HTTPException(200, detail={"code": 401, "msg": "用户认证失败", "data": {}})
