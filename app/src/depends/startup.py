import aio_pika
from redis.asyncio import Redis as aioredis

from core.settings import settings
from db import queue, redis
from services.queue import BaseRabbitQueue


async def startup():
    redis.client = aioredis.from_url(settings.REDIS.build_url())

    connection = await aio_pika.connect(
        host=settings.RABBITMQ.HOST,
        port=settings.RABBITMQ.PORT,
        login=settings.RABBITMQ.LOGIN,
        password=settings.RABBITMQ.PASSWORD,
    )

    queue.queue = await BaseRabbitQueue.init(connection=connection)
