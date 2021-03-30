# import os
#
# from tortoise.contrib.test import SimpleTestCase
#
# os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "tests.settings")
#
# from fast_tmp.conf import settings
#
#
# class TestCreatesuperuser(SimpleTestCase):  # fixme:create error.
#     async def test_createsuperuser(self):
#         from tortoise import Tortoise
#
#         await Tortoise.init(
#             db_url="sqlite://:memory:",
#             modules={"fast_tmp": settings.TORTOISE_ORM["apps"]["fast_tmp"]["models"]},
#         )
#         await Tortoise.generate_schemas()
#         from fastapi_cli import create_superuser
#
#         await create_superuser("admin", "admin")
