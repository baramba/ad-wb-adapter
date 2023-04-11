from logging.config import dictConfig

from arq.connections import RedisSettings
from core.logger import logging_conf
from core.settings import settings
from depends import shutdown as sd
from depends import startup as su
from tasks import tasks


async def startup(ctx: dict) -> None:
    # Переопределяем настройки логирования для arc
    dictConfig(logging_conf.dict())
    await su.startup()


async def shutdown(ctx: dict) -> None:
    await sd.shutdown()


class WorkerSettings:
    functions = tasks
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(host=settings.REDIS.HOST, port=settings.REDIS.PORT)
