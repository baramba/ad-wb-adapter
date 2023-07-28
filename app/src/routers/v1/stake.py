import uuid
from typing import Annotated

from fastapi import Depends, Header, Query, status
from fastapi.responses import ORJSONResponse, Response
from fastapi.routing import APIRouter

from core.settings import logger
from dto.official.stake import CampaignInfoDTO, CampaignsDTO, CampaignStatus, CampaignType
from exceptions.base import WBAError
from routers.utils import x_user_id
from schemas.v1.base import BaseResponse, BaseResponseEmpty, BaseResponseError, BaseResponseSuccess
from schemas.v1.stake import (
    ActualStakes,
    CampaignInfo,
    CampaignResponse,
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
        logger.error(e)
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
        logger.error(e)
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
        logger.error(e)
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
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
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
        logger.error(e)
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
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        await stake_service.pause_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
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
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        await stake_service.resume_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
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


@router.get(
    path="/campaigns",
    responses={
        status.HTTP_200_OK: {"model": CampaignsResponse},
    },
    summary="Метод для получения списка рекламных кампаний пользователя.",
    description="Метод позволяет позволяет получить список рекламных кампаний.",
)
async def campaigns(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    stake_service: StakeService = Depends(get_stake_service),
    type: CampaignType | None = Query(None, description="Тип рекламной кампании."),
    status: CampaignStatus | None = Query(None, description="Статус рекламной кампании."),
    limit: int | None = Query(None, description="Количество кампаний в ответе."),
) -> Response:
    try:
        campaigns: CampaignsDTO | None = await stake_service.campaigns(status=status, type=type, limit=limit)
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


@router.post(
    path="/intervals",
    responses={
        status.HTTP_200_OK: {"model": BaseResponseSuccess},
    },
    summary="Метод для изменения временных интервалов для показа рекламных кампаний.",
    description="Метод позволяет установить список временных интервалов для рекламной кампании.",
)
async def intervals(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
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
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description="Ошибка при установке временных интервалов. user_id={0}, wb_campaign_id={1}".format(
                    user_id,
                    wb_campaign_id,
                )
            ).dict()
        )


@router.get(
    path="/campaign",
    responses={
        status.HTTP_200_OK: {"model": CampaignResponse},
    },
    summary="Метод для получения информации о рекламной кампании.",
    description="""Метод позволяет позволяет получить информацию о рекламной кампании по id.
    <a href="https://openapi.wildberries.ru/#tag/Reklama/paths/~1adv~1v0~1advert/get">Ссылка на описание.</a>""",
)
async def campaign(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    campaign_id: int,
    stake_service: StakeService = Depends(get_stake_service),
) -> Response:
    try:
        campaign: CampaignInfoDTO | None = await stake_service.campaign(user_id=user_id, campaign_id=campaign_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при получении списка рекламных кампаний. user_id={user_id}"
            ).dict()
        )
    if not campaign:
        return ORJSONResponse(content=BaseResponseEmpty().dict())

    return ORJSONResponse(content=CampaignResponse(payload=CampaignInfo.parse_obj(campaign)).dict())
