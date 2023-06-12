import uuid

from fastapi import Depends, Query, status
from fastapi.responses import ORJSONResponse, Response
from fastapi.routing import APIRouter

from core.settings import logger
from dto.official.stake import CampaignsDTO, CampaignStatus, CampaignType
from exceptions.base import WBAError
from schemas.v1.base import BaseResponse, BaseResponseEmpty, BaseResponseError, BaseResponseSuccess
from schemas.v1.stake import (
    ActualStakes,
    Campaigns,
    CampaignsResponse,
    IntervalsRequest,
    Organic,
    OrganicResponse,
    ProductResponse,
    Products,
    StakeResponse,
)
from services.stake import StakeService, get_stake_service

router = APIRouter(prefix="/stake", tags=["stake"])


@router.get(
    path="/stakes",
    responses={
        status.HTTP_200_OK: {"model": StakeResponse},
    },
    summary="Метод для получения списка актуальных ставок.",
    description="Метод позволяет получить актуальные ставки по ключевой фразе.",
)
async def actual_stakes(
    keyword: str,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        actual_stakes = await stake_service.actual_stakes(keyword=keyword)
        stakes = ActualStakes.parse_obj(actual_stakes)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(content=BaseResponseError(description="Ошибка при получении актуальных ставок.").dict())

    if stakes.adverts is None:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=StakeResponse(payload=stakes).dict(by_alias=True))


@router.get(
    path="/products",
    responses={
        status.HTTP_200_OK: {"model": ProductResponse},
    },
    summary="Метод для получение информации о продуктах в регионе.",
    description="Метод позволяет получить информацию о продуктах в регионе.",
)
async def products_by_region(
    dest: str,
    nm: str,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        products_ = await stake_service.products_by_region(dest=dest, nm=nm)
        products = Products.parse_obj(products_)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(description="Ошибка при получении информации о продуктах в регионе.")
        )

    if not products.products:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=ProductResponse(payload=products).dict())


@router.get(
    path="/organic",
    responses={
        status.HTTP_200_OK: {"model": OrganicResponse},
    },
    summary="Метод для получение органической выдачи по региону.",
    description="Метод позволяет получить информацию о продуктах в регионе.",
)
async def organic_by_region(
    dest: str,
    query: str,
    resultset: str,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        organic_ = await stake_service.organic_by_region(
            dest=dest,
            query=query,
            resultset=resultset,
        )
        organic = Organic.parse_obj(organic_)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(content=BaseResponseError())

    if organic.time1 is None:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=OrganicResponse(payload=organic).dict())


@router.put(
    path="/rate",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для установки нового значения ставки.",
    description="Метод позволяет установить новое значение ставки на торгах.",
)
async def set_new_rate(
    wb_campaign_id: int,
    rate: int,
    user_id: uuid.UUID,
    stake_service: StakeService = Depends(get_stake_service),
    ad_type: CampaignType = CampaignType.SEARCH,
    param: int | None = None,
) -> Response:
    try:
        await stake_service.set_new_rate(
            rate=rate,
            wb_campaign_id=wb_campaign_id,
            ad_type=ad_type,
            user_id=user_id,
            param=param,
        )
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при установке нового значения ставки на торгах. wb_campaign_id={wb_campaign_id}"
            ).dict()
        )
    return ORJSONResponse(
        content=BaseResponseSuccess(
            description=f"Установлено новое значение ставки на торгах. wb_campaign_id={wb_campaign_id}"
        ).dict()
    )


@router.put(
    path="/pause",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для постановки кампании на паузу.",
    description="Метод позволяет поставить кампанию на паузу.",
)
async def pause_campaign(
    wb_campaign_id: int,
    user_id: uuid.UUID,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        await stake_service.pause_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при постановке кампании на паузу. wb_campaign_id={wb_campaign_id}"
            ).dict()
        )
    return ORJSONResponse(
        content=BaseResponseSuccess(description=f"Кампания поставлена на паузу. wb_campaign_id={wb_campaign_id}").dict()
    )


@router.put(
    path="/resume",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для возобновления работы рекламной кампании.",
    description="Метод позволяет возобновить работу рекламной кампании.",
)
async def resume_campaign(
    wb_campaign_id: int,
    user_id: uuid.UUID,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        await stake_service.resume_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при возобновлении кампании. wb_campaign_id={wb_campaign_id}"
            ).dict()
        )
    return ORJSONResponse(
        content=BaseResponseSuccess(
            description=f"Работа кампании успешно возобновлена. wb_campaign_id={wb_campaign_id}"
        ).dict()
    )


@router.put(
    path="/campaigns",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для получения списка рекламных кампаний пользователя.",
    description="Метод позволяет позволяет получить список рекламных кампаний.",
)
async def campaigns(
    user_id: uuid.UUID,
    stake_service: StakeService = Depends(get_stake_service),
    type: CampaignType | None = Query(None, description="Тип рекламной кампании."),
    status: CampaignStatus | None = Query(None, description="Статус рекламной кампании."),
) -> Response:
    try:
        campaigns: CampaignsDTO | None = await stake_service.campaigns(user_id=user_id, status=status, type=type)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при получении списка рекламных кампаний. user_id={user_id}"
            ).dict()
        )
    if not campaigns:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=CampaignsResponse(payload=Campaigns.parse_obj(campaigns)).dict())


@router.post(
    path="/intervals",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для изменения временных интервалов для показа рекламных кампаний.",
    description="Метод позволяет установить список временных интервалов для рекламной кампании.",
)
async def intervals(
    user_id: uuid.UUID,
    wb_campaign_id: int,
    body: IntervalsRequest,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        await stake_service.set_time_intervals(
            user_id=user_id,
            wb_campaign_id=wb_campaign_id,
            intervals=body.intervals,
            param=body.param,
        )
        return ORJSONResponse(content=BaseResponseSuccess().dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description="Ошибка при установке временных интервалов. user_id={0}, wb_campaign_id={1}".format(
                    user_id,
                    wb_campaign_id,
                )
            ).dict()
        )
