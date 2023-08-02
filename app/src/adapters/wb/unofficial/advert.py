from urllib.parse import quote

from fastapi import status
from httpx import HTTPStatusError
from pydantic import ValidationError

from adapters.wb.unofficial.wbadapter import WBAdapterUnofficial
from adapters.wb.utils import error_for_raise
from core.settings import logger
from dto.unofficial.advert import ActualStakesDTO, OrganicsDTO, ProductsDTO
from exceptions.base import WBAError
from schemas.v1.base import ResponseCode


class AdvertAdapterUnofficial(WBAdapterUnofficial):
    async def actual_stakes(self, keyword: str) -> ActualStakesDTO:
        """Метод возвращает список актуальных ставок по ключевой фразе."""

        url = "https://catalog-ads.wildberries.ru/api/v6/search"
        referer = f"https://www.wildberries.ru/catalog/0/search.aspx?search={quote(keyword)}"

        headers = {"Referer": referer}
        params = {"keyword": keyword}
        try:
            result = await self._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Ошибка при получении списка актуальных ставок.",
                error_class=WBAError,
            ) from e

        try:
            return ActualStakesDTO.parse_obj(result.json())
        except ValidationError as e:
            logger.error(str(e))
            raise WBAError(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="По запросу получены не валидные данные.",
            ) from e

    async def products_by_region(self, dest: str, nm: str) -> ProductsDTO:
        """Метод возвращает список продуктов по региону."""

        url = "https://card.wb.ru/cards/list"
        referer = "https://www.wildberries.ru/catalog/0/search.aspx?search"

        headers = {"Referer": referer}
        params = {
            "dest": dest,
            "nm": nm,
        }
        try:
            result = await self._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Ошибка при получении списка продуктов по региону.",
                error_class=WBAError,
            ) from e

        try:
            products = result.json()["data"]
            return ProductsDTO.parse_obj(products)
        except KeyError:
            logger.exception("Не удалось обработать результат запроса, полученный от WB.")
            return ProductsDTO()

    async def organic_by_region(self, dest: str, query: str, resultset: str) -> OrganicsDTO:
        """Метод возвращает список продуктов по региону."""

        url = "https://search.wb.ru/exactmatch/ru/male/v4/search"
        referer = "https://www.wildberries.ru/catalog/0/search.aspx? \
                    search=%D0%B2%D0%B5%D0%BB%D0%BE%D1%81%D0%B8%D0%BF%D0%B5%D0%B4"

        headers = {"Referer": referer}
        params = {
            "dest": dest,
            "query": query,
            "resultset": resultset,
        }
        try:
            result = await self._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Не удалось получить данные органической выдачи.",
                error_class=WBAError,
            ) from e
        try:
            products = result.json()["data"]["products"]
            return OrganicsDTO(products=products)
        except ValidationError as e:
            logger.error(f"Failed to process received data from Wildberries. error: {e}")
            raise WBAError(
                status_code=ResponseCode.ERROR,
                description=f"Не удалось обработать данные, полученные от WB. {e}",
            ) from e
        except KeyError:
            return OrganicsDTO(products=None)
