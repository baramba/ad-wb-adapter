from logging.config import dictConfig
from arq.connections import RedisSettings

from core.settings import settings
from depends import startup as su, shutdown as sd
from tasks import tasks
from core.logger import logging_conf


async def startup(ctx):
    # redefine arq logger conf
    dictConfig(logging_conf.dict())
    await su.startup()


async def shutdown(ctx):
    await sd.shutdown()


class WorkerSettings:
    functions = tasks
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(host=settings.REDIS.HOST, port=settings.REDIS.PORT)
