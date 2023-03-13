from redis.asyncio import Redis
from db import redis


async def get_redis() -> Redis:
    return redis.redis
