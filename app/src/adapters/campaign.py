import asyncio
import collections
import inspect
import math
from typing import Any
import backoff

from adapters.http_adapter import HTTPAdapter
from exceptions.base import WBACampaignError
from exceptions.campaign import (
    CampaignCreateError,
    CampaignInitError,
    CampaignStartError,
)
from httpx import HTTPStatusError

from schemas.v1.supplier import WbUserAuthData


class CampaignAdapter:
    def __init__(self, client: HTTPAdapter) -> None:
        self.client: HTTPAdapter = client
        self._auth_data: WbUserAuthData | None = None

    async def get_auth_data(self, attr_name: str) -> Any:
        attr: Any = getattr(self._auth_data, attr_name)
        return attr

    @property
    async def auth_data(self) -> WbUserAuthData | None:
        return self._auth_data

    @auth_data.setter
    async def auth_data(self, value: WbUserAuthData) -> None:
        self.client.headers["X-User-Id"] = await self.get_auth_data("wb_user_id")
        cookies = {
            "x-supplier-id-external": await self.get_auth_data("wb_supplier_id"),
            "WBToken": await self.get_auth_data("wb_token_access"),
        }
        self.client.headers.update(cookies)

        self._auth_data = value

    async def get_subject_id(self, nms: int) -> int:
        url: str = f"https://card.wb.ru/cards/detail?nm={nms}"

        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        headers.update(self.client.headers)

        try:
            result = await self.client._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при получении subject id."
            )
        subject_id: int = result.json()["data"]["products"][0]["subjectId"]
        return subject_id

    async def get_category(self, nms: int) -> str:
        subject_id: int = await self.get_subject_id(nms=nms)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects"

        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        headers.update(self.client.headers)

        try:
            result = await self.client._get(
                url=url,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при получении category."
            )
        category: str | None = None
        for item in result.json():
            if item["id"] == subject_id:
                category = item["name"]

        if not category:
            raise CampaignCreateError.init(
                result.status_code,
                "Не удалось получить название категории для subject_id={0}".format(
                    subject_id
                ),
            )

        return category

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def create_campaign(
        self,
        name: str,
        nms: list[int],
    ) -> int:
        """Создает рекламную кампанию."""
        kw_nms = collections.defaultdict(list)

        for kw, nms_ in [(await self.get_category(nms=item), item) for item in nms]:
            kw_nms[kw].append(nms_)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/save-ad"
        body = {
            "campaignName": name,
            "groups": [{"nms": v, "key_word": k} for k, v in kw_nms.items()],
        }
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        headers.update(self.client.headers)
        try:
            result = await self.client._post(
                url=url, body=body, headers=self._headers, cookies=self._cookies
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при создании компании."
            )

        return int(result.json()["id"])

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def get_campaign_budget(
        self,
        id: int,
    ) -> int:
        """Получает текущий размер бюджета рекламной кампании."""

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        headers.update(self.client.headers)

        try:
            result = await self.client._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code, "Ошибка при получении бюджета компании."
            )
        return int(result.json()["total"])

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def add_keywords_to_campaign(
        self,
        id: int,
        keywords: list,
    ) -> None:
        """Добавляет ключевые слова в рекламную кампанию."""
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        headers.update(self.client.headers)

        body = {"pluse": keywords}
        try:
            result = await self.client._post(url=url, body=body, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при добавлении ключевых слов."
            )

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def switch_on_fixed_list(
        self,
        id: int,
    ) -> None:
        """Включает использование фиксированных фраз в рекламной кампании."""
        url = (
            f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus?fixed=true"
        )
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        headers.update(self.client.headers)

        try:
            result = await self.client._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при включении фиксированных фраз."
            )

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def replenish_budget(
        self,
        id: int,
        amount: int,
    ) -> None:
        """Увеличивает бюджет кампании до заданного значения с округлением в большую сторону."""
        url: str = (
            f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget/deposit"
        )
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        headers.update(self.client.headers)

        budget_amount: int = await self.get_campaign_budget(id=id)
        new_budget_amount: int = amount

        if budget_amount >= amount:
            return

        if budget_amount != 0:
            new_budget_amount = max(100, math.ceil(budget_amount / 50) * 50)

        body = {"sum": new_budget_amount, "type": 0}

        try:
            result = await self.client._post(
                url=url,
                body=body,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code,
                "Ошибка при добавлении бюджета компании.",
            )

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def get_campaign_config(self, id: int) -> dict:
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        headers.update(self.client.headers)
        try:
            result = await self.client._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при получении конфигурации кампании."
            )

        return dict(result.json())

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=WBACampaignError,
        max_tries=5,
    )
    async def start_campaign(self, id: int) -> None:
        """Запускает рекламную кампанию.

        Arguments:
            id -- идентификатор кампании

        Raises:
            CampaignStartError.init: Ошибка запуска кампании.
        """
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        headers.update(self.client.headers)
        budget: int = await self.get_campaign_budget(id=id)
        config: dict = await self.get_campaign_config(id=id)
        config["budget"]["total"] = budget
        # Задержка, чтобы избежать - too many requests (429)
        await asyncio.sleep(1)
        try:
            result = await self.client._put(
                url=url,
                body=config,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при запуске кампании."
            )

    def __getattribute__(self, name: str) -> Any | None:
        #  Проверяем, что _auth_data is not None.
        att = getattr(self._obj, name)
        if hasattr(self._obj, name) and inspect.ismethod(att):
            if self._auth_data is None:
                raise ValueError("Значние атрибута auth_data = None.")
        return att
