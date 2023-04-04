import asyncio
import collections
import contextlib

from httpx import HTTPStatusError

from adapters.http_client import BaseAdapter
from exceptions.campaign import (
    CampaignCreateError,
    CampaignInitError,
    CampaignStartError,
)
from core.settings import logger


class CampaignAdapter(BaseAdapter):
    async def get_subject_id(self, nms: int) -> int:
        url = f"https://card.wb.ru/cards/detail?nm={nms}"
        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._get(url=url, method=__name__)
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                result.status_code, "Ошибка при получении subject id"
            )
        subject_id: int = result.json()["data"]["products"][0]["subjectId"]
        return subject_id

    async def get_keyword(self, nms: int) -> str:
        subject_id = await self.get_subject_id(nms=nms)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects"

        for _ in range(5):
            logger.info("{0}:{1};".format(__name__, url))
            with contextlib.suppress(HTTPStatusError):
                result = await self._get(url=url, method=__name__)
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                result.status_code, "Ошибка при получении subject keyword"
            )

        for item in result.json():
            if item["id"] == subject_id:
                requested_data: int = item["name"]
                return requested_data
        # todo raise error

    async def create_campaign(
        self,
        name: str,
        nms: list[int],
    ) -> int:
        kw_nms = collections.defaultdict(list)
        for kw, nms in [(await self.get_keyword(nms=item), item) for item in nms]:
            kw_nms[kw].append(nms)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/save-ad"
        body = {
            "campaignName": name,
            "groups": [{"nms": v, "key_word": k} for k, v in kw_nms.items()],
        }
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._post(
                    url=url, body=body, headers=headers, method=__name__
                )
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                result.status_code, "Ошибка при создании компании"
            )

        return result.json()["id"]

    async def get_campaign_budget(
        self,
        id: int,
    ) -> dict:
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }

        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._get(url=url, headers=headers, method=__name__)
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                result.status_code, f"Ошибка при получении бюджета компании"
            )
        return result.json()

    async def add_keywords_to_campaign(
        self,
        id: int,
        keywords: list,
    ):
        url = (
            f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus?fixed=true"
        )
        body = {"pluse": keywords}
        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._post(url=url, body=body, method=__name__)
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                result.status_code, "Ошибка при добавлении ключевых слов"
            )

    async def add_amount_to_campaign_budget(
        self,
        id: int,
        amount: int,
    ):
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget/deposit"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        body = {"sum": amount, "type": 0}
        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._post(
                    url=url, body=body, headers=headers, method=__name__
                )
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                result.status_code, "Ошибка при добавлении бюджета компании"
            )

    async def set_campaign_bet(
        self,
        id: int,
        bet: int,
    ) -> dict:
        budget = await self.get_campaign_budget(id=id)
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/save"
        bugdet_len = len(budget["place"])
        budget["budget"]["total"] = bet
        for i in range(bugdet_len):
            budget["place"][i]["price"] = bet // bugdet_len

        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._put(url=url, body=budget, method=__name__)
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                result.status_code, "Ошибка при установке ставки"
            )
        return budget

    async def start_campaign(self, id: int, budget: dict):
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        for _ in range(5):
            with contextlib.suppress(HTTPStatusError):
                result = await self._put(
                    url=url, body=budget, headers=headers, method=__name__
                )
                result.raise_for_status()
                break
            await asyncio.sleep(1)

        try:
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                result.status_code, "Ошибка при запуске компании"
            )
