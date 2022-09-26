import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "{{ random_ascii_string(64, punctuation=True) }}"

DEBUG = True

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://{{cookiecutter.project_slug}}.sqlite3",
    },
    'apps': {
        'fast_tmp': {
            'models': ['fast_tmp.models','{{cookiecutter.project_slug}}.models' ],  # 注册app.models
            'default_connection': 'default',
        }
    }
}
EXTRA_SCRIPT = []  # 自定义执行脚本