from abc import ABC, abstractmethod
from typing import Self

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel, AbstractExchange
from aio_pika.abc import AbstractQueue as PikaAbstractQueue
from aio_pika.abc import AbstractRobustConnection

from core.settings import settings


class AbstractQueue(ABC):
    @abstractmethod
    async def publish(self, routing_key: str, message_body: str, priority: int) -> None:
        pass

    @abstractmethod
    async def create_queue(self, routing_key: str) -> None:
        pass


class BaseRabbitQueue(AbstractQueue):
    connection: AbstractRobustConnection
    channel: AbstractChannel
    exchange: AbstractExchange

    @classmethod
    async def init(cls, connection: AbstractRobustConnection) -> Self:
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

    async def publish(self, routing_key: str, message_body: str, priority: int) -> None:
        message = Message(
            body=message_body.encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority,
        )

        await self.exchange.publish(
            message=message,
            routing_key=routing_key,
        )


class BaseQueue:
    def __init__(self, queue: AbstractQueue):
        self.queue = queue

    async def publish(self, routing_key: str, message: str, priority: int) -> None:
        await self.queue.publish(routing_key=routing_key, message_body=message, priority=priority)
