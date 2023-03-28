from depends.db.queue import get_queue
from services.queue import BaseQueue


async def get_queue_service():
    return BaseQueue(queue=await get_queue())
