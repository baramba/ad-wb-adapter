import uuid

from arq import ArqRedis

from fastapi import APIRouter, Depends, status

from depends.arq import get_arq
from dto.campaign import CreateCampaignDTO
from schemas.v1.base import RequestQueuedResponse
from schemas.v1.campaign import CreateCampaignResponse

router = APIRouter(prefix='/campaigns', tags=['campaigns'])


@router.post(
    path='',
    responses={
        status.HTTP_202_ACCEPTED: {'model': RequestQueuedResponse},
        status.HTTP_201_CREATED: {'model': CreateCampaignResponse}
    },
    description='Create campaign',
)
async def create_campaign(
        campaign: CreateCampaignDTO,
        arq: ArqRedis = Depends(get_arq),
):
    job_id = uuid.uuid4()

    await arq.enqueue_job(
        'create_campaign',
        job_id,
        campaign,
    )
    return RequestQueuedResponse(job_id=job_id)
