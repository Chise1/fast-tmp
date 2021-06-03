from tortoise import Tortoise
from tortoise.contrib.test import TestCase as TC
from tortoise.contrib.test import TransactionTestContext, _restore_default


class TestCase(TC):
    """
        An asyncio capable test class that will ensure that each test will be run at
    separate transaction that will rollback on finish.

    This is a fast test runner. Don't use it if your test uses transactions.
    修复tortoise测试类的一个bug.
    """

    connection_name: str = "models"

    async def _run_outcome(self, outcome, expecting_failure, testMethod) -> None:
        _restore_default()
        self.__db__ = Tortoise.get_connection(self.connection_name)
        if self.__db__.capabilities.supports_transactions:
            connection = self.__db__._in_transaction().connection
            async with TransactionTestContext(connection):
                await super()._run_outcome(outcome, expecting_failure, testMethod)
        else:
            await super()._run_outcome(outcome, expecting_failure, testMethod)
