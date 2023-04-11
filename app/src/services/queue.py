from abc import ABC, abstractmethod
from typing import Self

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange
from aio_pika.abc import AbstractQueue as PikaAbstractQueue
from core.settings import settings


class AbstractQueue(ABC):
    @abstractmethod
    async def publish(self, queue_name: str, message_body: str, priority: int) -> None:
        pass

    @abstractmethod
    async def create_queue(self, queue_name: str) -> None:
        pass


class BaseRabbitQueue(AbstractQueue):
    connection: AbstractConnection
    channel: AbstractChannel
    exchange: AbstractExchange

    @classmethod
    async def init(cls, connection: AbstractConnection) -> Self:
        self = cls()
        self.connection = connection
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.get_exchange(name=settings.RABBITMQ.EXCHANGE)
        return self

    async def create_queue(self, queue_name: str) -> None:
        queue: PikaAbstractQueue = await self.channel.declare_queue(
            name=queue_name, durable=True, arguments={"x-max-priority": 10}
        )
        await queue.bind(exchange=self.exchange, routing_key=queue_name)

    async def publish(self, queue_name: str, message_body: str, priority: int) -> None:
        message = Message(
            body=message_body.encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority,
        )

        await self.exchange.publish(
            message=message,
            routing_key=queue_name,
        )


class BaseQueue:
    def __init__(self, queue: AbstractQueue):
        self.queue = queue

    async def publish(self, queue_name: str, message: str, priority: int) -> None:
        await self.queue.publish(
            queue_name=queue_name, message_body=message, priority=priority
        )
