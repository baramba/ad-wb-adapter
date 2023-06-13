from httpx import HTTPStatusError
from pydantic import ValidationError, parse_obj_as

from adapters.wb.official.wbadapter import WBAdapter
from core.settings import logger, settings
from dto.official.stake import (
    ActualStakeDTO,
    ActualStakesDTO,
    CampaignDTO,
    CampaignsDTO,
    CampaignStatus,
    CampaignType,
    IntervalDTO,
)
from exceptions.base import WBAError


class StakeAdapter(WBAdapter):
    async def actual_stakes(self, type: int, param: int) -> ActualStakesDTO:
        """Метод возвращает список актуальных ставок по ключевой фразе."""

        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/cpm"
        params = {
            "type": type,
            "param": param,
        }

        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении списка актуальных ставок.",
            ) from e
        stakes = parse_obj_as(list[ActualStakeDTO], result.json())
        return ActualStakesDTO(stakes=stakes)

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
        Raises:
            WBAError:
        """

        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/cpm"

        body = {
            "advertId": advert_id,
            "type": type,
            "cpm": cpm,
            "param": param,
        }

        try:
            result = await self._post(url=url, body=body)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"Ошибка при установке нового значения ставки. body={body}. ",
            ) from e

    async def start_campaign(self, id: int) -> None:
        """Метод позволяет запустить рекламную кампанию.

        Arguments:
            id -- идентификатор реклмной кампании.

        Raises:
            WBAError: _description_
        """

        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/start"

        params = {"id": id}

        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"Ошибка при старте рекламной капании. wb_campaign_id={id}.",
            ) from e

    async def pause_campaign(self, id: int) -> None:
        """Метод позволяет поставить рекламную кампанию на паузу.

        Arguments:
            id -- идентификатор реклмной кампании.

        Raises:
            WBAError: _description_
        """

        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/pause"

        params = {"id": id}

        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"Ошибка при постановке на паузу рекламной капании. wb_campaign_id={id}.",
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

        Raises:
            WBAError:
        """

        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/adverts"

        params = {
            "status": status,
            "type": type,
            "limit": limit,
            "offset": offset,
            "order": order,
            "direction": direction,
        }
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
                description="Ошибка при получении списка рекламных кампаний.",
            ) from e
        except ValidationError as e:
            logger.error("Не удалось обработать данные, полученные в ответ на запрос.")
            logger.error(f"error={e.errors()}")
            raise WBAError(
                description="Ошибка при получении списка рекламных кампаний.",
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

        Raises:
            WBAError: _description_
        """
        url = f"{settings.WILDBERRIES.OFFICIAL_API_ADV_URL}/intervals"
        body = {
            "advertId": wb_campaign_id,
            "intervals": [interval.dict() for interval in intervals],
            "param": param,
        }

        try:
            result = await self._post(url=url, body=body)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка изменения интервала показа РК.",
            ) from e
