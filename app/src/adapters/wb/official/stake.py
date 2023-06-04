from httpx import HTTPStatusError
from pydantic import parse_obj_as

from adapters.wb.official.wbadapter import WBAdapter
from dto.official.stake import ActualStakeDTO, ActualStakesDTO
from exceptions.base import WBAError


class StakeAdapter(WBAdapter):
    async def actual_stakes(self, type: int, param: int) -> ActualStakesDTO:
        """Метод возвращает список актуальных ставок по ключевой фразе."""

        url = "https://advert-api.wb.ru/adv/v0/cpm"
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

        url = "https://advert-api.wb.ru/adv/v0/cpm"

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

        url = "https://advert-api.wb.ru/adv/v0/start"

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

        url = "https://advert-api.wb.ru/adv/v0/pause"

        params = {"id": id}

        try:
            result = await self._get(url=url, params=params)
            result.raise_for_status()
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description=f"Ошибка при постановке на паузу рекламной капании. wb_campaign_id={id}.",
            ) from e
