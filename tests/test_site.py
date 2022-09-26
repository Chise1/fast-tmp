# import os
#
# from tortoise import connections
# from tortoise.contrib.test import TestCase, TransactionTestContext
#
# os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "tests.settings")
# from fastapi_cli import __createuser as createuser
#
#
#
# class TestCreatesuperuser(TestCase):  # fixme:create error.
#     async def asyncSetUp(self) -> None:
#         await super(TestCase, self).asyncSetUp()
#         self._db = connections.get("fast_tmp")
#         self._transaction = TransactionTestContext(self._db._in_transaction().connection)
#         await self._transaction.__aenter__()  # type: ignore
#
#     async def test_createsuperuser(self):
#         await createuser("admin","admin")
