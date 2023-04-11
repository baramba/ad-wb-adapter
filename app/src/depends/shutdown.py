from core.settings import logger
from db.redis import get_redis


async def shutdown() -> None:
    try:
        get_redis().close()
    except NameError:
        logger.warning("Redis's client is None")
