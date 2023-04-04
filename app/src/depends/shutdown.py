from db.redis import get_redis
from core.settings import logger


async def shutdown():
    try:
        get_redis().close()
    except NameError:
        logger.warning("Redis's client is None")
