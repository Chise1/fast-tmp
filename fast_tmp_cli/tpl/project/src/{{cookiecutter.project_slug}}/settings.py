import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "{{ random_ascii_string(64, punctuation=True) }}" # 如果出现\x，则会报错，需要删除\x

DEBUG = True

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://src.sqlite3",
    },
    'apps': {
        'fast_tmp': {
            'models': ['fast_tmp.models','src.models' ],  # 注册app.models
            'default_connection': 'default',
        }
    }
}
EXTRA_SCRIPT = []  # 自定义执行脚本