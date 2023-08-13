import uuid
from typing import Annotated

from arq import ArqRedis
from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.responses import ORJSONResponse, Response

from core.settings import logger
from depends.arq import get_arq
from dto.official.advert import CampaignInfoDTO, CampaignsDTO, CampaignStatus, CampaignType
from dto.unofficial.campaign import CampaignCreateDTO, ReplenishBugetRequestDTO, ReplenishSourceType
from exceptions.base import WBAError
from routers.utils import x_user_id
from schemas.v1.advert import (
    CampaignBudget,
    CampaignBudgetResponse,
    CampaignInfo,
    CampaignResponse,
    Campaigns,
    CampaignsResponse,
)
from schemas.v1.base import BaseResponse, BaseResponseEmpty, BaseResponseError, JobResult, RequestQueuedResponse
from schemas.v1.campaign import Budget, CreateCampaignResponse, ReplenishBugetResponse
from services.campaign import CampaignService, get_campaign_service
from tasks.create_full_campaign import CampaignCreateFullTask
from tasks.restart_create_campaign import СontinueCreateCampaignTask

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    path="/full",
    responses={
        status.HTTP_202_ACCEPTED: {"model": RequestQueuedResponse},
        status.HTTP_201_CREATED: {"model": JobResult[CreateCampaignResponse]},
    },
    summary="Возвращает 200 в случае успешного создания задачи.",
    description="Создает и запускает рекламную кампанию на стороне wildberries.",
)
async def create_full_campaign(
    campaign: CampaignCreateDTO,
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
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


@router.put(
    path="/continue",
    responses={
        status.HTTP_202_ACCEPTED: {"model": RequestQueuedResponse},
        status.HTTP_201_CREATED: {"model": JobResult[CreateCampaignResponse]},
    },
    summary="Метод позволяет продолжить создание рекламной кампании на стороне wildberries.",
    description="Возвращает 200 в случае успешного создания задачи.",
)
async def continue_create_campaign(
    campaign: CampaignCreateDTO,
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    wb_campaign_id: int,
    routing_key: Annotated[str, Header()],
    arq: ArqRedis = Depends(get_arq),
) -> RequestQueuedResponse:
    job_id = uuid.uuid4()

    await arq.enqueue_job(
        СontinueCreateCampaignTask.continue_create_campaign.__qualname__,
        job_id=job_id,
        campaign=campaign,
        routing_key=routing_key,
        user_id=x_user_id,
        wb_campaign_id=wb_campaign_id,
    )
    return RequestQueuedResponse(job_id=job_id)


@router.get(
    path="/{wb_campaign_id}",
    responses={
        status.HTTP_200_OK: {"model": CampaignResponse},
    },
    summary="Метод для получения информации о рекламной кампании.",
    description="""
Метод позволяет позволяет получить информацию о рекламной кампании по id.
[https://advert-api.wb.ru/adv/v0/advert]\
(https://advert-api.wb.ru/adv/v0/advert)
""",
)
async def campaign(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    wb_campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
) -> Response:
    try:
        campaign: CampaignInfoDTO | None = await campaign_service.campaign(campaign_id=wb_campaign_id)
        if not campaign:
            return ORJSONResponse(
                content=BaseResponseEmpty(
                    description="В ответ на запрос информации о рекламной кампании получен пустой ответ."
                ).dict()
            )
        return ORJSONResponse(content=CampaignResponse(payload=CampaignInfo.parse_obj(campaign)).dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(description="Не удалось получить информацию о рекламной кампании.").dict()
        )


@router.get(
    path="",
    responses={
        status.HTTP_200_OK: {"model": CampaignsResponse},
    },
    summary="Метод для получения списка рекламных кампаний пользователя.",
    description="""Метод позволяет позволяет получить список рекламных кампаний.",
[https://advert-api.wb.ru/adv/v0/adverts]\
(https://advert-api.wb.ru/adv/v0/adverts)
""",
)
async def campaigns(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    campaign_service: CampaignService = Depends(get_campaign_service),
    type: CampaignType | None = Query(None, description="Тип рекламной кампании."),
    status: CampaignStatus | None = Query(None, description="Статус рекламной кампании."),
    limit: int | None = Query(None, description="Количество кампаний в ответе."),
) -> Response:
    try:
        campaigns: CampaignsDTO | None = await campaign_service.campaigns(status=status, type=type, limit=limit)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при получении списка рекламных кампаний. user_id={user_id}"
            ).dict()
        )
    if not campaigns:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=CampaignsResponse(payload=Campaigns.parse_obj(campaigns)).dict())


@router.get(
    path="/{wb_campaign_id}/budget",
    responses={
        status.HTTP_200_OK: {"model": CampaignBudgetResponse},
    },
    summary="Метод для получения бюджета рекламной кампании.",
    description="""
Метод позволяет позволяет получить бюджет рекламной кампании.
[https://advert-api.wb.ru/adv/v1/budget]\
(https://advert-api.wb.ru/adv/v1/budget)
""",
)
async def budget(
    wb_campaign_id: int,
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    campaign_service: CampaignService = Depends(get_campaign_service),
) -> Response:
    try:
        budget = await campaign_service.budget(wb_campaign_id=wb_campaign_id)
        if not budget:
            return ORJSONResponse(content=BaseResponseEmpty().dict())
        return ORJSONResponse(content=CampaignBudgetResponse(payload=CampaignBudget(budget=budget.total)).dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(description="Ошибка при получении бюджета рекламной кампании.").dict()
        )


@router.post(
    path="/{wb_campaign_id}/deposit",
    responses={
        status.HTTP_200_OK: {"model": ReplenishBugetResponse},
    },
    summary="Метод для пополнения бюджета кампании.",
    description="""
Метод позволяет пополнить бюджет рекламной кампании со счета или баланса пользователя.
[https://advert-api.wb.ru/adv/v1/budget/deposit]\
(https://advert-api.wb.ru/adv/v1/budget/deposit)
""",
)
async def deposit(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    wb_campaign_id: int,
    amount: int,
    type: ReplenishSourceType = Query(description="0 - Счет, 1 - Баланс"),
    campaign_service: CampaignService = Depends(get_campaign_service),
) -> Response:
    try:
        budget = await campaign_service.replenihs_budget(
            ReplenishBugetRequestDTO(wb_campaign_id=wb_campaign_id, type=type, amount=amount)
        )
        return ORJSONResponse(content=ReplenishBugetResponse(payload=Budget(budget=budget)).dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при пополнении бюджета рекламной кампании. wb_campaign_id={wb_campaign_id}"
            ).dict()
        )
