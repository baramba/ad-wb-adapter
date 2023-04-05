import collections

from httpx import HTTPStatusError

from adapters.wb_http_client import BaseAdapter
from exceptions.campaign import (
    CampaignCreateError,
    CampaignInitError,
    CampaignStartError,
)


class CampaignAdapter(BaseAdapter):
    async def get_subject_id(self, nms: int) -> int:
        url = f"https://card.wb.ru/cards/detail?nm={nms}"

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

        for item in result.json():
            if item["id"] == subject_id:
                requested_data: str = item["name"]
                return requested_data
        # todo raise error

    async def create_campaign(
        self,
        name: str,
        nms: list[int],
    ) -> int:
        kw_nms = collections.defaultdict(list)
        for kw, nms in [(await self.get_category(nms=item), item) for item in nms]:
            kw_nms[kw].append(nms)

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

        return result.json()["id"]

    async def get_campaign_budget(
        self,
        id: int,
    ) -> dict:
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }

        try:
            result = await self._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code, f"Ошибка при получении бюджета компании."
            )
        return result.json()

    async def add_keywords_to_campaign(
        self,
        id: int,
        keywords: list,
    ):
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus"
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
    ):
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

    async def set_campaign_budget(
        self,
        id: int,
        amount: int,
    ):
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget/deposit"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        body = {"sum": amount, "type": 0}

        try:
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

        try:
            result = await self._put(url=url, body=budget)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignInitError.init(
                e.response.status_code, "Ошибка при установке ставки."
            )
        return budget

    async def start_campaign(self, id: int, budget: dict):
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }

        try:
            result = await self._put(
                url=url,
                body=budget,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при запуске компании."
            )
