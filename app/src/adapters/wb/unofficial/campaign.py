import asyncio
import collections
import math

from httpx import HTTPStatusError

from adapters.wb.unofficial.wbadapter import WBAdapterUnofficial
from adapters.wb.utils import error_for_raise
from dto.unofficial.campaign import CampaignConfigDTO, CampaignStatus, ReplenishBugetRequestDTO
from exceptions.base import WBAError
from exceptions.campaign import CampaignCreateError, CampaignInitError, CampaignStartError


class CampaignAdapterUnofficial(WBAdapterUnofficial):
    async def get_subject_id(self, nms: int) -> int:
        url: str = "https://card.wb.ru/cards/detail"

        params = {"nm": nms}
        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}
        try:
            result = await self._get(url=url, headers=headers, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при получении subject id. nms={nms}",
                error_class=CampaignCreateError,
            ) from e

        subject_id: int = result.json()["data"]["products"][0]["subjectId"]
        return subject_id

    async def get_category(self, nms: int) -> str:
        subject_id: int = await self.get_subject_id(nms=nms)

        url = "https://cmp.wildberries.ru/backend/api/v2/search/supplier-subjects"

        headers = {"Referer": "https://cmp.wildberries.ru/campaigns/create/search"}

        try:
            result = await self._get(
                url=url,
                headers=headers,
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при получении category. nms = {nms}",
                error_class=CampaignCreateError,
            ) from e

        category: str | None = None
        for item in result.json():
            if item["id"] == subject_id:
                category = item["name"]

        if not category:
            raise CampaignCreateError(
                status_code=result.status_code,
                description="Не удалось получить название категории для subject_id={0}".format(subject_id),
            )

        return category

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

        try:
            result = await self._post(url=url, body=body, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при создании компании. name={name}, body={body}",
                error_class=CampaignCreateError,
            ) from e

        return int(result.json()["id"])

    async def get_campaign_budget(
        self,
        id: int,
    ) -> int:
        """Возвращает текущий размер бюджета рекламной кампании."""

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/budget"
        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"}

        try:
            result = await self._get(url=url, headers=headers)
            result.raise_for_status()
            total = int(result.json()["total"])
            if isinstance(total, int):
                return total
            raise ValueError("Ошибка при получении бюджета компании. wb_campaign_id={id}")
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при получении бюджета компании. wb_campaign_id={id}",
                error_class=CampaignInitError,
            ) from e

    async def add_keywords_to_campaign(
        self,
        id: int,
        keywords: list,
    ) -> None:
        """Добавляет ключевые слова в рекламную кампанию."""
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus"

        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"}

        body = {"pluse": keywords}
        try:
            result = await self._post(url=url, body=body, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при добавлении ключевых слов. keywords={keywords}",
                error_class=CampaignInitError,
            ) from e

    async def switch_on_fixed_list(
        self,
        id: int,
    ) -> None:
        """Включает использование фиксированных фраз в рекламной кампании."""
        url = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/set-plus?fixed=true"
        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"}

        try:
            result = await self._get(url=url, headers=headers)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description="Ошибка при включении опции использования фиксированных фраз.",
                error_class=CampaignInitError,
            ) from e

    async def replenish_budget(self, replenish: ReplenishBugetRequestDTO) -> None:
        """Увеличивает бюджет кампании до заданного значения с округлением в большую сторону."""
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{replenish.wb_campaign_id}/budget/deposit"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{replenish.wb_campaign_id}"
        }

        budget_amount: int = await self.get_campaign_budget(id=replenish.wb_campaign_id)
        new_budget_amount: int = replenish.amount

        if budget_amount >= new_budget_amount:
            return

        if budget_amount != 0:
            new_budget_amount = max(100, math.ceil(budget_amount / 50) * 50)

        body = {"sum": new_budget_amount, "type": replenish.type}

        try:
            await self._post(
                url=url,
                body=body,
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при добавлении бюджета кампании. body={body}",
                error_class=CampaignInitError,
            ) from e

    async def replenish_budget_at(self, replenish: ReplenishBugetRequestDTO) -> None:
        """Увеличивает бюджет кампании на X рублей."""
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{replenish.wb_campaign_id}/budget/deposit"
        headers = {
            "Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{replenish.wb_campaign_id}"
        }

        body = {"sum": replenish.amount, "type": replenish.type}

        try:
            await self._post(
                url=url,
                body=body,
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при пополнении бюджета рекламной кампании. text = {e.response.content.decode()}",
                error_class=WBAError,
            ) from e

    async def get_campaign_config(self, id: int) -> CampaignConfigDTO:
        """Возвращает текущию конфигурацию компании."""
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"
        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"}

        try:
            result = await self._get(url=url, headers=headers)
            return CampaignConfigDTO.parse_obj(result.json())
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при получении конфигурации кампании. wb_campaign_id={id}",
                error_class=WBAError,
            ) from e

    async def start_campaign(self, id: int) -> None:
        """Запускает рекламную кампанию.

        Arguments:
            id -- идентификатор кампании

        Raises:
            CampaignStartError.init: Ошибка запуска кампании.
        """
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"}

        budget_amount: int = await self.get_campaign_budget(id=id)
        await asyncio.sleep(0.5)
        config: CampaignConfigDTO = await self.get_campaign_config(id=id)
        config.budget.total = budget_amount
        # Задержка, чтобы избежать - too many requests (429)
        await asyncio.sleep(0.5)
        try:
            await self._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при запуске кампании. campaign_id={id}",
                error_class=CampaignStartError,
            ) from e

    async def update_campaign_config(self, id: int, config: CampaignConfigDTO) -> None:
        """Обновляет конфигурацию кампании.

        Arguments:
            config -- новое конфигурация кампании.
        """

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/placement"

        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"}

        try:
            await self._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при обновлении конфигурации кампании. wb_campaign_id={id}",
                error_class=WBAError,
            ) from e

    async def update_campaign_rate(self, id: int, config: CampaignConfigDTO) -> None:
        """Устанавливает новое значение ставки рекламной кампании.

        Arguments:
            config -- новое конфигурация кампании.
        """

        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/save"

        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/all/edit/search/{id}"}

        try:
            await self._put(
                url=url,
                body=config.dict(),
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при обновлении размера ставки на торгах. wb_campaign_id={id}",
                error_class=WBAError,
            ) from e

    async def pause_campaign(self, id: int) -> CampaignStatus:
        """Ставит рекламную кампанию на паузу.

        Arguments:
            id -- идентификатор кампании

        Raises:
            WBAError: в случае получения ошибки от wildberries
        """
        url: str = f"https://cmp.wildberries.ru/backend/api/v2/search/{id}/pause"

        headers = {"Referer": f"https://cmp.wildberries.ru/campaigns/list/active/edit/search/{id}"}

        try:
            await self._get(
                url=url,
                headers=headers,
            )
        except HTTPStatusError as e:
            raise error_for_raise(
                status_code=e.response.status_code,
                description=f"Ошибка при постановке кампании на паузу. wb_campaign_id={id}",
                error_class=WBAError,
            ) from e

        return CampaignStatus.PAUSED
