from http import HTTPStatus

from httpx import HTTPStatusError
from pydantic import ValidationError, parse_obj_as

from adapters.wb.official.wbadapter import WBAdapter
from core.settings import logger, settings
from dto.official.advert import (
    ActualStakeDTO,
    ActualStakesDTO,
    BalanceDTO,
    BudgetDTO,
    CampaignDTO,
    CampaignInfoDTO,
    CampaignsDTO,
    CampaignStatus,
    CampaignType,
    IntervalDTO,
)
from exceptions.base import WBAError


class AdvertAdapter(WBAdapter):
    async def actual_stakes(self, type: int, param: int) -> ActualStakesDTO:
        """Метод возвращает список актуальных ставок по ключевой фразе."""

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/cpm"
        params = {
            "type": type,
            "param": param,
        }
        error_desc = "Не удалось получить список актуальных ставок."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
            stakes = parse_obj_as(list[ActualStakeDTO], result.json())
            return ActualStakesDTO(stakes=stakes)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e
        except ValidationError as e:
            error_desc = f"{error_desc}. error={e.errors()}"
            logger.error(error_desc)
            raise WBAError(
                description=error_desc,
            ) from e

    async def change_rate(self, advert_id: int, type: int, cpm: int, param: int) -> None:
        """Метод позволяет установить новое значние ставки на торгах.

        Arguments:
            advert_id -- Идентификатор РК, где меняется ставка;
            type -- Тип РК, где меняется ставка:
                    5 - реклама в карточке товара
                    6 - реклама в поиске
                    7 - реклама в рекомендациях на главной странице
            cpm -- Новое значение ставки
            param -- Параметр, для которого будет внесено изменение (является значением subjectId или setId в
                     зависимости от типа РК)
        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/cpm"

        body = {
            "advertId": advert_id,
            "type": type,
            "cpm": cpm,
            "param": param,
        }
        error_desc = "Не удалось установить новое значение ставки."
        try:
            result = await self._post(url=url, body=body)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"{error_desc} body={body}. ",
            ) from e

    async def start_campaign(self, id: int) -> None:
        """Метод позволяет запустить рекламную кампанию.

        Arguments:
            id -- идентификатор реклмной кампании.

        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/start"

        params = {"id": id}
        error_desc = "Не удалось запустить рекламную кампанию."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e

    async def pause_campaign(self, id: int) -> None:
        """Метод позволяет поставить рекламную кампанию на паузу.

        Arguments:
            id -- идентификатор реклмной кампании.

        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/pause"

        params = {"id": id}
        error_desc = "Не удалось поставить рекламную кампанию на паузу."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e

    async def campaigns(
        self,
        status: CampaignStatus | None,
        type: CampaignType | None,
        limit: int | None = None,
        offset: int | None = None,
        order: str = "create",
        direction: str = "desc",
    ) -> CampaignsDTO | None:
        """Метод позволяет получить список рекламных кампаний пользователя WB.

        Arguments:
            status -- Статус РК:
                        7 - РК завершена
                        9 - идут показы
                        11 - РК на паузе

        Keyword Arguments:
            type -- Тип РК (default: {6})
                    4 - реклама в каталоге
                    5 - реклама в карточке товара
                    6 - реклама в поиске
                    7 - реклама в рекомендациях на главной странице
            limit -- Количество кампаний в ответе (default: {None})
            offset -- Смещение относительно первой РК (default: {None})
            order -- Порядок (default: {"create"})
                create (по времени создания РК),
                change (по времени последнего изменения РК),
                id (по идентификатору РК),
            direction -- Направление (default: {"desc"})
                        desc (от большего к меньшему)
                        asc (от меньшего к большему)
        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/adverts"

        params = {
            "status": status,
            "type": type,
            "limit": limit,
            "offset": offset,
            "order": order,
            "direction": direction,
        }
        error_desc = "Не удалось получить списк рекламных кампаний."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
            data = result.json()
            if not data:
                return None
            campaigns = parse_obj_as(list[CampaignDTO], result.json())
            return CampaignsDTO(campaigns=campaigns)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e
        except ValidationError as e:
            error_desc = f"{error_desc}. error={e.errors()}"
            logger.error(error_desc)
            raise WBAError(
                description=error_desc,
            ) from e

    async def set_time_intervals(self, wb_campaign_id: int, intervals: list[IntervalDTO], param: int) -> None:
        """Метод позволяет установить время показа рекламной кампании.

        Arguments:
            wb_campaign_id -- идентификатор кампании.
            intervals -- временные интервалы:
                        begin -- время начала показов, по 24 часовой схеме ("begin": 15);
                        end -- время окончания показов, по 24 часовой схеме ("end": 21);
            param -- Параметр, для которого будет внесено изменение, должен быть значением menuId (для РК в каталоге),
                     subjectId (для РК в поиске и рекомендациях) или setId (для РК в карточке товара).

        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/intervals"
        body = {
            "advertId": wb_campaign_id,
            "intervals": [interval.dict() for interval in intervals],
            "param": param,
        }
        error_desc = "Не удалось изменить интервал показа рекламной кампании."
        try:
            result = await self._post(url=url, body=body)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e

    async def campaign(self, id: int) -> CampaignInfoDTO | None:
        """Метод позволяет получить информацию о рекламной кампании.

        Arguments:
            id -- идентификатор рекламной кампании

        Returns:
            Возвращает информацию о рекламной кампании или None, если она не была найдена.
        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v0/advert"

        params = {"id": id}
        error_desc = "Не удалось получить информацию о рекламной кампании."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
            if result.status_code == HTTPStatus.NO_CONTENT:
                return None
            data = result.json()
            return CampaignInfoDTO.parse_obj(data) if data else None
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e
        except ValidationError as e:
            error_desc = f"{error_desc}. error={e.errors()}"
            logger.error(error_desc)
            raise WBAError(
                description=error_desc,
            ) from e

    async def balance(self) -> BalanceDTO:
        """Метод позволяет получить информацию о балансе пользователя.

        Returns:
            Возвращает информацию о балансе пользователя.
        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v1/balance"
        error_desc = "Не удалось получить информацию о балансе пользователя."
        try:
            result = await self._get(url=url)
            result.raise_for_status()
            data = result.json()
            return BalanceDTO.parse_obj(data)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e
        except ValidationError as e:
            error_desc = f"{error_desc}. error={e.errors()}"
            logger.error(error_desc)
            raise WBAError(
                description=error_desc,
            ) from e

    async def budget(self, wb_campaign_id: int) -> BudgetDTO:
        """Метод позволяет получить информацию о бюджете рекламной кампании.

        Returns:
            Возвращает текущий размер бюджета рекламной кампании.
        """

        url = f"{settings.WBADAPTER.WB_OFFICIAL_API_ADV_URL}/v1/budget"
        params = {"id": wb_campaign_id}
        error_desc = "Не удалось получить информацию о бюджете рекламной кампании."
        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
            data = result.json()
            return BudgetDTO.parse_obj(data)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=error_desc,
            ) from e
        except ValidationError as e:
            error_desc = f"{error_desc}. error={e.errors()}"
            logger.error(error_desc)
            raise WBAError(
                description=error_desc,
            ) from e
