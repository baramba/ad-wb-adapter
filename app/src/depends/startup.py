import aio_pika
from core.settings import settings
from db import queue, redis
from redis.asyncio import Redis
from services.queue import BaseRabbitQueue


async def startup() -> None:
    redis.client = Redis.from_url(settings.REDIS.build_url())
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ.HOST,
        port=settings.RABBITMQ.PORT,
        login=settings.RABBITMQ.LOGIN,
        password=settings.RABBITMQ.PASSWORD,
    )

    queue.queue = await BaseRabbitQueue.init(connection=connection)
