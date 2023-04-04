from redis.asyncio import Redis

client: Redis | None = None

async def get_redis() -> Redis | None:
    return client
