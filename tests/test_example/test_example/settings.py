import os

import dotenv

dotenv.load_dotenv()

# import sentry_sdk
# from sentry_sdk.integrations.redis import RedisIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = os.getenv("DEBUG") == "True"

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://:memory:",
    },
    "apps": {
        "fast_tmp": {
            "models": ["test_example.models", "fast_tmp.models", "aerich.models"],  # 注册app.models
            "default_connection": "default",
        }
    },
}
EXTRA_SCRIPT = []  # 自定义执行脚本
# redis配置
# REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
# REDIS_PORT = os.getenv("REDIS_PORT", 6379)
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
# REDIS = {
#     "host": REDIS_HOST,
#     "port": REDIS_PORT,
#     "password": REDIS_PASSWORD,
#     "db": 2,
#     "encoding": "utf-8",
# }
# sentry配置
# sentry_sdk.init(
#     dsn=os.getenv("SENTRY_DSN"),
#     environment=os.getenv("ENVIRONMENT", "development"),
#     integrations=[RedisIntegration()],
# )
# logging
# LOGGER = logging.getLogger("example")
# if DEBUG:
#     LOGGER.setLevel(logging.DEBUG)
# else:
#     LOGGER.setLevel(logging.INFO)
# sh = logging.StreamHandler(sys.stdout)
# sh.setLevel(logging.DEBUG)
# sh.setFormatter(
#     logging.Formatter(
#         fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S",
#     )
# )
# LOGGER.addHandler(sh)
