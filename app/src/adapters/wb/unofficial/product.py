from fastapi import status
from httpx import HTTPStatusError
from pydantic import ValidationError, parse_obj_as

from adapters.wb.unofficial.wbadapter import WBAdapterUnofficial
from adapters.wb.utils import error_for_raise
from core.settings import logger
from dto.unofficial.product import CategoriesDTO, CategoryDTO, ProductRequestBodyDTO, ProductsDTO, ProductsSubjectDTO
from exceptions.base import WBAError


class ProductAdapter(WBAdapterUnofficial):
    async def products(self) -> ProductsDTO:
        """Метод возвращает список продуктовых карточек пользователя."""

        url = "https://seller-content.wildberries.ru/ns/viewer/content-card/viewer/tableListv4"
        referer = "https://seller.wildberries.ru/"

        headers = {"Referer": referer}
        body = ProductRequestBodyDTO().dict()
        try:
            result = await self._post(url=url, headers=headers, body=body)
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Ошибка при получении продуктовых карточек пользователя.",
                error_class=WBAError,
            ) from e

        try:
            return ProductsDTO.parse_obj(result.json())
        except ValidationError as e:
            logger.error(e)
            raise WBAError(
                status_code=status.HTTP_400_BAD_REQUEST,
                description=f"Не удалось обработать результат запроса продуктовых карточек. result={result.json()}",
            ) from e

    async def categories(self) -> CategoriesDTO:
        url = "https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects"
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}

        try:
            result = await self._get(url=url, headers=headers)
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Ошибка при получении списка категорий.",
                error_class=WBAError,
            ) from e
        categories = parse_obj_as(list[CategoryDTO], result.json())
        return CategoriesDTO(categories=categories)

    async def products_by_subject(self, subject_id: int) -> ProductsSubjectDTO:
        """Метод возвращает список продуктовых карточек пользователя по subject_id."""

        url = "https://cmp.wildberries.ru/backend/api/v2/search/products"
        referer = "https://cmp.wildberries.ru/campaigns/create/search"

        headers = {"Referer": referer}
        params = {"subject": subject_id}
        try:
            result = await self._get(url=url, headers=headers, params=params)
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при получении продуктовых карточек пользователя. subject_id={subject_id}",
                error_class=WBAError,
            ) from e
        try:
            products = result.json()[0]["products"]
            return ProductsSubjectDTO.parse_obj(products)
        except ValidationError as e:
            logger.error(e)
            raise WBAError(
                status_code=status.HTTP_400_BAD_REQUEST,
                description=f"Не удалось обработать результат запроса продуктовых карточек. result={result.json()}",
            ) from e
