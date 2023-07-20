from logging.config import dictConfig

from arq.connections import RedisSettings
from core.settings import log_config, logger, settings
from depends import shutdown as sd
from depends import startup as su
from tasks import tasks


async def startup(ctx: dict) -> None:
    # Переопределяем настройки логирования для arc
    dictConfig(config=log_config)
    logger.setLevel(settings.WBADAPTER.LOG_LEVEL)
    await su.startup()


async def shutdown(ctx: dict) -> None:
    await sd.shutdown()


class WorkerSettings:
    functions = tasks
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(host=settings.REDIS.HOST, port=settings.REDIS.PORT, database=1)
