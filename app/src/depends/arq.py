from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from core.settings import settings


async def get_arq() -> ArqRedis:
    return await create_pool(
        RedisSettings(host=settings.REDIS.HOST, port=settings.REDIS.PORT),
    )
