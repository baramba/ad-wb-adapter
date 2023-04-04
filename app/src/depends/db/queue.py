from db import queue
from services.queue import AbstractQueue


async def get_queue() -> AbstractQueue:
    if queue.queue is None:
        raise Exception("get_queue(), queue is None.")
    return queue.queue
