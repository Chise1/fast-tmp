import os

import dotenv

dotenv.load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = os.getenv("DEBUG") == "True"
SECRET_KEY = "asdfasdfaserbbdgv"

SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")  # 服务器运行的IP或者域名
TORTOISE_ORM = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "fast_tmp": {
            "models": ["fast_tmp.models", "tests.testmodels"],  # 注册app.models
            "default_connection": "default",
        }
    },
}
