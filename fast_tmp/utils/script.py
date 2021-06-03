import logging

from tortoise import Tortoise

from fast_tmp.conf import settings


class RegisterTortoise(object):
    def __init__(self):
        self.config = settings.TORTOISE_ORM

    async def __aenter__(self):
        await Tortoise.init(config=self.config)
        logging.info("Tortoise-ORM started, %s, %s", Tortoise._connections, Tortoise.apps)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await Tortoise.close_connections()
        logging.info("Tortoise-ORM shutdown")
