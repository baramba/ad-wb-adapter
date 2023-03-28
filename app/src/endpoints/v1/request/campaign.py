import uuid

from arq import ArqRedis

from fastapi import APIRouter, Depends, status, Header

from depends.arq import get_arq
from dto.campaign import CreateCampaignDTO
from schemas.v1.base import RequestQueuedResponse, JobResult
from schemas.v1.campaign import CreateCampaignResponse

router = APIRouter(prefix='/campaigns', tags=['campaigns'])


@router.post(
    path='/full',
    responses={
        status.HTTP_202_ACCEPTED:
            {'model': RequestQueuedResponse},
        status.HTTP_201_CREATED:
            {'model': JobResult[CreateCampaignResponse]}
    },
    description='Create campaign',
)
async def create_full_campaign(
        campaign: CreateCampaignDTO,
        routing_key: str = Header(),
        arq: ArqRedis = Depends(get_arq),
):
    job_id = uuid.uuid4()

    await arq.enqueue_job(
        'create_full_campaign',
        job_id,
        campaign,
        routing_key
    )
    return RequestQueuedResponse(job_id=job_id)
