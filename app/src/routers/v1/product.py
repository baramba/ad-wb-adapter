import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse

from core.settings import logger
from exceptions.base import WBAError
from routers.utils import x_user_id
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
    description="""
Метод позволяет получить список продуктовых карточек пользователя.
[https://cmp.wildberries.ru/backend/api/v2/search/products]\
(https://cmp.wildberries.ru/backend/api/v2/search/products)
""",
)
async def products(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
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
    description="""
Метод позволяет получить список категорий пользователя WB.
[https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects]\
(https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects)
""",
)
async def categories(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
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
