import asyncio
import collections
import math
from typing import Any
import backoff

from adapters.http_adapter import HTTPAdapter
from dto.campaign import CampaignConfigDTO, CampaignStatus
from exceptions.base import WBACampaignError, WBAError
from exceptions.campaign import (
    CampaignCreateError,
    CampaignInitError,
    CampaignStartError,
)
from httpx import HTTPStatusError

from dto.supplier import WbUserAuthDataDTO


class CampaignAdapter:
    def __init__(self, client: HTTPAdapter) -> None:
        self.client: HTTPAdapter = client
        self._auth_data: WbUserAuthDataDTO | None = None

    @property
    def auth_data(self) -> WbUserAuthDataDTO | None:
        return self._auth_data

    @auth_data.setter
    def auth_data(self, auth_data: WbUserAuthDataDTO) -> None:
        self._auth_data = auth_data
        self.client.headers["X-User-Id"] = str(self._auth_data.wb_user_id)
        self.client.cookies["x-supplier-id-external"] = str(
            self._auth_data.wb_supplier_id
        )
        self.client.cookies["WBToken"] = str(self._auth_data.wb_token_access)

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def get_subject_id(self, nms: int) -> int:
        url: str = "https://card.wb.ru/cards/detail"

        params = {"nm": nms}
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        headers.update(self.client.headers)

        try:
            result = await self.client._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при получении subject id."
            )
        subject_id: int = result.json()["data"]["products"][0]["subjectId"]
        return subject_id

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
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
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
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
                url=url,
                body=body,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignCreateError.init(
                e.response.status_code, "Ошибка при создании компании."
            )

        return int(result.json()["id"])

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def get_campaign_budget(
        self,
        id: int,
    ) -> int:
        """Возвращает текущий размер бюджета рекламной кампании."""

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
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
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
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
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
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
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
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def get_campaign_config(self, id: int) -> CampaignConfigDTO:
        """Возвращает текущию конфигурацию компании."""
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

        return CampaignConfigDTO.parse_obj(result.json())

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
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
        budget_amount: int = await self.get_campaign_budget(id=id)
        await asyncio.sleep(0.5)
        config: CampaignConfigDTO = await self.get_campaign_config(id=id)
        config.budget.total = budget_amount
        # Задержка, чтобы избежать - too many requests (429)
        await asyncio.sleep(0.5)
        try:
            result = await self.client._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise CampaignStartError.init(
                e.response.status_code, "Ошибка при запуске кампании."
            )

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def update_campaign_config(self, id: int, config: CampaignConfigDTO) -> None:
        """Обновляет конфигурацию кампании.

        Arguments:
            config -- новое конфигурация кампании.
        """

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        headers.update(self.client.headers)

        try:
            result = await self.client._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при обновлении конфигурации кампании.",
            )

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def update_campaign_rate(self, id: int, config: CampaignConfigDTO) -> None:
        """Устанавливает новое значение ставки рекламной кампании.

        Arguments:
            config -- новое конфигурация кампании.
        """

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/save"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"
        }
        headers.update(self.client.headers)

        try:
            result = await self.client._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при обновлении размера ставки на торгах.",
            )

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=WBACampaignError, max_tries=5
    )
    async def pause_campaign(self, id: int) -> CampaignStatus:
        """Ставит рекламную кампанию на паузу.

        Arguments:
            id -- идентификатор кампании

        Raises:
            WBAError: в случае получения ошибки от wildberries
        """
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/pause"

        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"
        }
        headers.update(self.client.headers)

        try:
            result = await self.client._get(
                url=url,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"Ошибка при постановке кампании на паузу. wb_campaign_id={id}",
            )
        return CampaignStatus.PAUSED

    def __getattribute__(self, name: str) -> Any | None:
        #  Проверяем, что _auth_data is not None.
        attr = super().__getattribute__(name)
        if callable(attr) and super().__getattribute__("_auth_data") is None:
            raise ValueError(
                "Значние атрибута CampaignAdapter.auth_data = None. Для корректной работы адаптера установите \
                авторизационные данные."
            )
        return super().__getattribute__(name)
