from fastapi import HTTPException
from starlette import status

credentials_exception = HTTPException(  # 登录报错
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="未登录或权限过期",
    headers={"WWW-Authenticate": "Bearer"},
)
no_permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="权限不够",
    headers={"WWW-Authenticate": "Bearer"},
)
password_exception = HTTPException(  # 登录报错
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="账户或密码错误",
)
