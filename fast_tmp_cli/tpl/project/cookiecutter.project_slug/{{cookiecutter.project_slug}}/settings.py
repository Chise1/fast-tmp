import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.getenv("SECRET_KEY") # todo 环境变量默认配置该参数

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