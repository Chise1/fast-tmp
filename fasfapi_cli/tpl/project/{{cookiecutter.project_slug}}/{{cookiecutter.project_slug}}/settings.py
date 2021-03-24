import os
import dotenv

# import sentry_sdk
# from sentry_sdk.integrations.redis import RedisIntegration

dotenv.load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = os.getenv("DEBUG") == "True"
PROJECT_CODE = "AUDIT"
SECRET_KEY = "asdfadagre"  # user密码的密钥
# 注意：默认情况下创建的是同步的url，需要自己改为异步的驱动，
DATABASE_URL = os.getenv(
    "DATABASE_URL")  # 数据库链接，例如：postgresql+asyncpg://postgres:mininet@localhost/fasttmp

SERVER_HOST = os.getenv("SERVER_HOST", '127.0.0.1')  # 服务器运行的IP或者域名
# 存储静态文件的地方，主要是配合amis
STATIC_ROOT = "static"
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


# CAS账户登录依赖
# CAS_LOGIN_URL = "/cas-lo"
# 前端cookie存储session的配置，需要安装额外依赖包
# CAS_SESSION_SECRET = "!secret"
# 如果使用了cas依赖，则需要配置
# CAS_SERVER_URL = "http://127.0.0.1:8000/cas"
