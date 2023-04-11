import asyncio
import collections
import math

from adapters.wb_http_client import BaseAdapter
from exceptions.campaign import (
    CampaignCreateError,
    CampaignInitError,
    CampaignStartError,
)
from httpx import HTTPStatusError


class CampaignAdapter(BaseAdapter):
    async def get_subject_id(self, nms: int) -> int:
        url: str = f"https://card.wb.ru/cards/detail?nm={nms}"

        try:
            result = await self._get(url=url)
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

        try:
            result = await self._get(url=url)
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

    async def create_campaign(
        self,
        name: str,
        nms: list[int],
    ) -> int:
        kw_nms = collections.defaultdict(list)

        for kw, nms_ in [(await self.get_category(nms=item), item) for item in nms]:
            kw_nms[kw].append(nms_)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/save-ad"
        body = {
            "campaignName": name,
            "groups": [{"nms": v, "key_word": k} for k, v in kw_nms.items()],
        }
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}

        try:
            result = await self._post(url=url, body=body, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при создании компании."
            )

        return int(result.json()["id"])

    async def get_campaign_budget(
        self,
        id: int,
    ) -> int:
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }

        try:
            result = await self._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code, "Ошибка при получении бюджета компании."
            )
        return int(result.json()["total"])

    async def add_keywords_to_campaign(
        self,
        id: int,
        keywords: list,
    ) -> None:
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus"
        body = {"pluse": keywords}
        try:
            result = await self._post(url=url, body=body)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при добавлении ключевых слов."
            )

    async def switch_on_fixed_list(
        self,
        id: int,
    ) -> None:
        url = (
            f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus?fixed=true"
        )

        try:
            result = await self._get(url=url)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при включении фиксированных фраз."
            )

    async def replenish_budget(
        self,
        id: int,
        amount: int,
    ) -> None:
        url: str = (
            f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget/deposit"
        )
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }

        budget_amount: int = await self.get_campaign_budget(id=id)
        new_budget_amount: int = amount

        if budget_amount >= amount:
            return

        if budget_amount != 0:
            new_budget_amount = max(100, math.ceil(budget_amount / 50) * 50)

        body = {"sum": new_budget_amount, "type": 0}

        try:
            result = await self._post(
                url=url,
                body=body,
                headers=headers,
            )
            result = await self._post(
                url=url,
                body=body,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code, "Ошибка при добавлении бюджета компании."
            )

    async def get_campaign_config(self, id: int) -> dict:
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }

        try:
            result = await self._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при получении конфигурации кампании."
            )

        return dict(result.json())

    async def start_campaign(self, id: int) -> None:
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        budget: int = await self.get_campaign_budget(id=id)
        config: dict = await self.get_campaign_config(id=id)
        config["budget"]["total"] = budget
        # Задержка, чтобы избежать - too many requests (429)
        await asyncio.sleep(1)
        try:
            result = await self._put(
                url=url,
                body=config,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при запуске кампании."
            )
