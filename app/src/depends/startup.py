import aio_pika
from redis.asyncio import Redis as aioredis

from core.settings import settings
from db import redis,queue
from services.queue import BaseRabbitQueue


async def startup():
    redis.redis = aioredis.from_url(settings.REDIS.build_url())

    connection = await aio_pika.connect(
        host=settings.RABBITMQ.HOST,
        port=settings.RABBITMQ.PORT,
        login=settings.RABBITMQ.LOGIN,
        password=settings.RABBITMQ.PASSWORD
    )

    queue.queue = await BaseRabbitQueue.init(connection=connection)
