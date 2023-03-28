from db import queue
from services.queue import AbstractQueue


async def get_queue() -> AbstractQueue:
    return queue.queue