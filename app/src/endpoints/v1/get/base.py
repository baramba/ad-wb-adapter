import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from redis.asyncio import Redis

from depends.db.redis import get_redis
from schemas.v1.base import JobResult

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.get(
    path='/{job_id}',
    responses={
        status.HTTP_200_OK: {'model': JobResult},
    },
    description='Get job result by id',
)
async def get_order_by_id(
        job_id: uuid.UUID,
        redis: Redis = Depends(get_redis),
):
    result = await redis.get(name=str(job_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return JobResult.parse_raw(result)
