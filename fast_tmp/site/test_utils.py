from fast_tmp.models import User
from .utils2 import get_columns_from_model
def t():
    get_columns_from_model(User,("username","password","groups"))

print(":hel;lo")