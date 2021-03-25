# -*- encoding: utf-8 -*-
"""
@File    : global_settings.py
@Time    : 2020/12/20 23:44
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_AUTH = True
EXPIRES_DELTA = 30
AUTH_USER_MODEL = "models.User"

FAST_TMP_URL = "/fast"
STATIC_URL = "/static"
SERVER_URL = "http://localhost:8000"
CAS_SESSION_COOKIE_NAME = "/cas_session_cookie"
CAS_LOGIN_URL = "/cas-login"
CAS_LOGOUT_URL = "/cas-logout"
CAS_LOGOUT_CALLBACK_URL = "/cas-loutout-callback"
HOME_URL = "/"
CAS_CHECK_USER = "fast_tmp.func.get_userinfo"  # 检查用户的
STATIC_APP = "static"
