from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from core.settings import settings


async def get_arq() -> ArqRedis:
    redis_dns = f"redis://{settings.REDIS.HOST}:{settings.REDIS.PORT}?db={settings.REDIS.DATABASE}"

    return await create_pool(
        RedisSettings.from_dsn(redis_dns),
    )
