from httpx import HTTPStatusError
from fastapi import status
from pydantic import ValidationError
from adapters.http_adapter import HTTPAdapter
from dto.stake import ActualStakesDTO, OrganicDTO, ProductsDTO
from exceptions.base import WBAError
from urllib.parse import quote
from core.settings import logger


class StakeAdapter:
    def __init__(self, client: HTTPAdapter) -> None:
        self.client: HTTPAdapter = client

    async def actual_stakes(self, keyword: str) -> ActualStakesDTO:
        """Метод возвращает список актуальных ставок по ключевой фразе."""

        url = "https://catalog-ads.wildberries.ru/api/v5/search"
        referer = (
            f"https://www.wildberries.ru/catalog/0/search.aspx?search={quote(keyword)}"
        )

        headers = {"Referer": referer}
        # TODO: может перенести это в HTTPAdapter ?
        headers.update(self.client.headers)
        params = {"keyword": keyword}
        try:
            result = await self.client._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении списка актуальных ставок.",
            )

        try:
            return ActualStakesDTO.parse_obj(result.json())
        except ValidationError as e:
            logger.error(str(e))
            raise WBAError(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="По запросу получены не валидные данные.",
            )

    async def products_by_region(self, dest: str, nm: str) -> ProductsDTO:
        """Метод возвращает список продуктов по региону."""

        url = "https://card.wb.ru/cards/list"
        referer = "https://www.wildberries.ru/catalog/0/search.aspx?search"

        headers = {"Referer": referer}
        # TODO: может перенести это в HTTPAdapter ?
        headers.update(self.client.headers)
        params = {
            "dest": dest,
            "nm": nm,
        }
        try:
            result = await self.client._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении списка актуальных ставок.",
            )
        try:
            products = result.json()["data"]
            return ProductsDTO.parse_obj(products)
        except KeyError:
            logger.exception(
                "Не удалось обработать результат запроса, полученный от WB."
            )
            return ProductsDTO(products=None)

    async def organic_by_region(
        self, dest: str, query: str, resultset: str
    ) -> OrganicDTO:
        """Метод возвращает список продуктов по региону."""

        url = "https://search.wb.ru/exactmatch/ru/male/v4/search"
        referer = "https://www.wildberries.ru/catalog/0/search.aspx? \
                    search=%D0%B2%D0%B5%D0%BB%D0%BE%D1%81%D0%B8%D0%BF%D0%B5%D0%B4"

        headers = {"Referer": referer}
        # TODO: может перенести это в HTTPAdapter ?
        headers.update(self.client.headers)
        params = {
            "dest": dest,
            "query": query,
            "resultset": resultset,
        }
        try:
            result = await self.client._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении списка поисковой выдачи.",
            )
        try:
            product = result.json()["data"]["products"][0]
            return OrganicDTO.parse_obj(product)
        except (IndexError, KeyError):
            logger.exception(
                "Не удалось обработать результат запроса, полученный от WB."
            )
            return OrganicDTO()
