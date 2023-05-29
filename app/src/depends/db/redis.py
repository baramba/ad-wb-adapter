from redis.asyncio import Redis
from core.settings import logger
from db import redis


async def get_redis() -> Redis:
    client: Redis | None = redis.client
    if not client:
        logger.error("redis.client is None.")
        raise Exception("redis.client is None.")
    return client
