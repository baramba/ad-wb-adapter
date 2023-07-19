import uuid
from typing import Annotated

from arq import ArqRedis
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.responses import ORJSONResponse, Response

from core.settings import logger
from depends.arq import get_arq
from dto.unofficial.campaign import CampaignCreateDTO, ReplenishBugetRequestDTO, ReplenishSourceType
from exceptions.base import WBAError
from schemas.v1.base import BaseResponse, BaseResponseError, JobResult, RequestQueuedResponse
from schemas.v1.campaign import Budget, CreateCampaignResponse, ReplenishBugetResponse
from services.campaign import CampaignService, get_campaign_service
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


@router.post(
    path="/deposit",
    responses={
        status.HTTP_200_OK: {"model": ReplenishBugetResponse},
    },
    description="Метод для пополнения бюджета кампании.",
    summary="Метод позволяет пополнить бюджет рекламной кампании со счета или баланса пользователя.",
)
async def deposit(
    wb_campaign_id: int,
    amount: int,
    user_id: Annotated[uuid.UUID, Header()],
    type: ReplenishSourceType = Query(description="0 - Счет, 1 - Баланс"),
    campaign_service: CampaignService = Depends(get_campaign_service),
) -> Response:
    try:
        budget = await campaign_service.replenihs_budget(
            ReplenishBugetRequestDTO(wb_campaign_id=wb_campaign_id, type=type, amount=amount)
        )
        return ORJSONResponse(content=ReplenishBugetResponse(payload=Budget(amount=budget)).dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при пополнении бюджета рекламной кампании. wb_campaign_id={wb_campaign_id}"
            ).dict()
        )
