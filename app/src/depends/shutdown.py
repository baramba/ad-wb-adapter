from db import redis


async def shutdown():
    await redis.close()
