import uuid

from core.settings import logger
from exceptions.base import WBAError
from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import ORJSONResponse
from schemas.v1.base import BaseResponse, BaseResponseError
from schemas.v1.product import Categories, CategoryResponse, ProductsSubject, ProductSubjectResponse
from services.product import ProductService, get_product_service

router = APIRouter(prefix="/product", tags=["product"])


@router.get(
    path="/products",
    responses={
        status.HTTP_200_OK: {"model": ProductSubjectResponse},
    },
    summary="Метод для получения списка продуктовых карточек.",
    description="Метод позволяет получить список продуктовых карточек пользователя WB.",
)
async def products(
    user_id: uuid.UUID,
    subject_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> Response:
    try:
        products = await product_service.products(user_id=user_id, subject_id=subject_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при получении списка продуктов пользователя. user_id={user_id}"
            ).dict()
        )

    return ORJSONResponse(content=ProductSubjectResponse(payload=ProductsSubject.parse_obj(products)).dict())


@router.get(
    path="/categories",
    responses={
        status.HTTP_200_OK: {"model": CategoryResponse},
    },
    summary="Метод для получения списка категорий.",
    description="Метод позволяет получить список категорий пользователя WB.",
)
async def categories(
    user_id: uuid.UUID = Query(),
    product_service: ProductService = Depends(get_product_service),
) -> Response:
    try:
        categories = await product_service.categories(user_id=user_id)
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(
                description=f"Ошибка при получении списка категорий пользователя. user_id={user_id}"
            ).dict()
        )

    return ORJSONResponse(content=CategoryResponse(payload=Categories.parse_obj(categories)).dict())
