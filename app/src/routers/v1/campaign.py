import uuid
from typing import Annotated

from arq import ArqRedis
from fastapi import APIRouter, Depends, Header, status

from depends.arq import get_arq
from dto.unofficial.campaign import CampaignCreateDTO
from schemas.v1.base import JobResult, RequestQueuedResponse
from schemas.v1.campaign import CreateCampaignResponse
from tasks.create_full_campaign import CampaignCreateFullTask

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    path="/full",
    responses={
        status.HTTP_202_ACCEPTED: {"model": RequestQueuedResponse},
        status.HTTP_201_CREATED: {"model": JobResult[CreateCampaignResponse]},
    },
    description="Создает и запускает рекламную кампанию на стороне wildberries.",
    summary="Возвращает 200 в случае успешного создания задачи.",
)
async def create_full_campaign(
    campaign: CampaignCreateDTO,
    user_id: Annotated[uuid.UUID, Header()],
    routing_key: Annotated[str, Header()],
    arq: ArqRedis = Depends(get_arq),
) -> RequestQueuedResponse:
    job_id = uuid.uuid4()

    await arq.enqueue_job(
        CampaignCreateFullTask.create_full_campaign.__qualname__,
        job_id,
        campaign,
        routing_key,
        user_id,
    )
    return RequestQueuedResponse(job_id=job_id)
