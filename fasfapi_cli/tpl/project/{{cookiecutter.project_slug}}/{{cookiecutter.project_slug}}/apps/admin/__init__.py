# 在这里创建fastapi_admin的项目，然后继承写下相关的api？？
from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings

app = AmisAPI(
    title="admin",
    debug=settings.DEBUG,
)
