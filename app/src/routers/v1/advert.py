import uuid
from typing import Annotated

from fastapi import Depends, status
from fastapi.responses import ORJSONResponse, Response
from fastapi.routing import APIRouter
from pydantic import parse_obj_as

from core.settings import logger
from dto.official.advert import CampaignType
from exceptions.base import WBAError
from routers.utils import x_user_id
from schemas.v1.advert import (
    ActualStakes,
    Config,
    ConfigResponse,
    IntervalsRequest,
    Organic,
    OrganicResponse,
    Organics,
    ProductResponse,
    Products,
    StakeResponse,
)
from schemas.v1.base import BaseResponse, BaseResponseEmpty, BaseResponseError, BaseResponseSuccess
from services.advert import AdvertService, get_advert_service

router = APIRouter(prefix="/stake", tags=["stake"])


@router.get(
    path="/stakes",
    responses={
        status.HTTP_200_OK: {"model": StakeResponse},
    },
    summary="Метод для получения списка актуальных ставок.",
    description="""
Метод позволяет получить актуальные ставки по ключевой фразе.
[https://catalog-ads.wildberries.ru/api/v6/search?keyword=]\
(https://catalog-ads.wildberries.ru/api/v6/search?keyword=)
""",
)
async def actual_stakes(
    keyword: str,
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        actual_stakes = await advert_service.actual_stakes(keyword=keyword)
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
    summary="Метод для получения информации о продуктах в регионе.",
    description="Метод позволяет получить информацию о продуктах в регионе.",
)
async def products_by_region(
    dest: str,
    nm: str,
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        products_ = await advert_service.products_by_region(dest=dest, nm=nm)
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
    description="""
Метод позволяет получить информацию о продуктах в регионе.
[https://search.wb.ru/exactmatch/ru/male/v4/search?dest=&query=&resultset=catalog]\
(https://search.wb.ru/exactmatch/ru/male/v4/search?dest=&query=&resultset=catalog)
""",
)
async def organic_by_region(
    dest: str,
    query: str,
    resultset: str,
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        organic = await advert_service.organic_by_region(
            dest=dest,
            query=query,
            resultset=resultset,
        )

        if not organic.products:
            return ORJSONResponse(content=BaseResponseEmpty().dict())

        products = parse_obj_as(list[Organic], organic.products)
        organics = Organics(products=products)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content=BaseResponseError().dict())

    return ORJSONResponse(content=OrganicResponse(payload=organics).dict())


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
    advert_service: AdvertService = Depends(get_advert_service),
    ad_type: CampaignType = CampaignType.SEARCH,
    param: int | None = None,
) -> Response:
    try:
        await advert_service.set_new_rate(
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
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        await advert_service.pause_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
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
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        await advert_service.resume_campaign(wb_campaign_id=wb_campaign_id, user_id=user_id)
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


@router.put(
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
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        await advert_service.set_time_intervals(
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
    path="/config",
    responses={
        status.HTTP_200_OK: {"model": ConfigResponse},
    },
    summary="Метод для получение конфигурационных параметров.",
    description="""
Метод позволяет получить:
- минимальное значение бюджета;
[https://cmp.wildberries.ru/backend/api/v5/configvalues]\
(https://cmp.wildberries.ru/backend/api/v5/configvalues)
""",
)
async def config(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    advert_service: AdvertService = Depends(get_advert_service),
) -> Response:
    try:
        config = await advert_service.config_values()
        return ORJSONResponse(content=ConfigResponse(payload=Config.parse_obj(config)).dict())
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content=BaseResponseError().dict())
