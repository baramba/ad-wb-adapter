import aio_pika
from aio_pika.abc import AbstractRobustConnection
from redis.asyncio import Redis

from core.settings import settings
from db import queue, redis
from services.queue import BaseRabbitQueue


async def startup() -> None:
    redis.client = Redis.from_url(settings.REDIS.build_url())
    connection: AbstractRobustConnection = await aio_pika.connect_robust(
        host=settings.RABBITMQ.HOST,
        port=settings.RABBITMQ.PORT,
        login=settings.RABBITMQ.LOGIN,
        password=settings.RABBITMQ.PASSWORD,
    )
    queue.queue = await BaseRabbitQueue.init(connection=connection)
