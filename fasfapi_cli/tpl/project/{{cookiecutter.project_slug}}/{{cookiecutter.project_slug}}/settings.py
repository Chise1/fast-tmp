import os
import dotenv

# import sentry_sdk
# from sentry_sdk.integrations.redis import RedisIntegration

dotenv.load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = os.getenv("DEBUG") == "True"
SECRET_KEY = os.getenv("SECRET_KEY")

SERVER_HOST = os.getenv("SERVER_HOST", '127.0.0.1')  # 服务器运行的IP或者域名
TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.aiomysql',
            'credentials': {
                'host': os.getenv("DB_HOST"),
                'port': os.getenv("DB_PORT"),
                'user': os.getenv("DB_USER"),
                'password': os.getenv("DB_PASSWORD"),
                'database': os.getenv("DB_NAME"),
            }
        },
    },
    'apps': {
        'models': {
            'models': [],  # 注册app.models
            'default_connection': 'default',
        }
    }
}

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
