from datetime import datetime
from enum import IntEnum

from schemas.common import BaseOrjsonModel


class ActualStakeDTO(BaseOrjsonModel):
    id: int
    cpm: int


class ActualStakesDTO(BaseOrjsonModel):
    stakes: list[ActualStakeDTO] | None


class CampaignType(IntEnum):
    """Тип рекламной кампании.

    Values:
        4 - реклама в каталоге,
        5 - реклама в карточке товара,
        6 - реклама в поиске,
        7 - реклама в рекомендациях на главной странице.
    """

    CATALOG = 4
    CARD = 5
    SEARCH = 6
    RECOMMEND = 7
    AUTO = 8
    SEARCH_CATALOG = 9


class CampaignStatus(IntEnum):
    """Статус рекламнйо кампании.

    Values:
        4 - готова к запуску,
        7 - РК завершена,
        8 - отказался,
        9 - идут показы,
        11 - РК на паузе.
    """

    READY_START = 4
    FINISHED = 7
    REFUSED = 8
    ACTIVE = 9
    PAUSED = 11


class CampaignDTO(BaseOrjsonModel):
    advertId: int
    name: str
    type: CampaignType
    status: CampaignStatus
    dailyBudget: int
    createTime: datetime
    changeTime: datetime
    startTime: datetime
    endTime: datetime


class CampaignInterval(BaseOrjsonModel):
    begin: int
    end: int


class NMS(BaseOrjsonModel):
    nm: int
    active: bool


class CampaignParam(BaseOrjsonModel):
    intervals: list[CampaignInterval] | None
    price: int
    nms: list[NMS]
    active: bool | None
    menuId: int | None
    menuName: str | None
    subjectName: str | None
    subjectId: int | None
    setId: int | None
    setName: str | None


class CampaignInfoDTO(CampaignDTO):
    name: str
    params: list[CampaignParam] | None


class CampaignsDTO(BaseOrjsonModel):
    campaigns: list[CampaignDTO]


class IntervalDTO(BaseOrjsonModel):
    begin: int
    end: int


class IntervalsDTO(BaseOrjsonModel):
    intervals: list[IntervalDTO]


class BudgetDTO(BaseOrjsonModel):
    # Поле не используется. Значение всегда 0.
    cash: int
    # Поле не используется. Значение всегда 0.
    netting: int
    # Бюджет рекламной кампании, ₽
    total: int


class BalanceDTO(BaseOrjsonModel):
    # Счёт, рублей
    balance: int
    # Баланс, рублей
    net: int
    # Бонусы, рублей
    bonus: int | None
