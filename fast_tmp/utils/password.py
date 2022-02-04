import binascii
import hashlib
from typing import Optional

from fast_tmp.conf import settings


def make_password(raw_password: str) -> str:
    """
    加密密码,返回加密的密码值和随机盐
    """
    password = hashlib.pbkdf2_hmac(
        "sha256", raw_password.encode("utf-8"), settings.SECRET_KEY.encode("utf-8"), 16
    )  # 随机生成盐值
    return binascii.hexlify(password).decode()


def verify_password(raw_password: str, password: Optional[str]) -> bool:
    """
    验证密码是否正确
    :param raw_password:要验证的密码
    :param password:数据库存储的密码
    """
    if not password or not raw_password:
        return False
    random_salt = settings.SECRET_KEY.encode("utf-8")
    raw_password_bytes = hashlib.pbkdf2_hmac(
        "sha256", raw_password.encode("utf-8"), random_salt, 16
    )
    if binascii.hexlify(raw_password_bytes).decode() == password:
        return True
    else:
        return False
