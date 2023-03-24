from core.settings import settings
from db import redis
from redis.asyncio import Redis as aioredis


async def startup():
    redis.redis = aioredis.from_url(settings.REDIS.build_url())
