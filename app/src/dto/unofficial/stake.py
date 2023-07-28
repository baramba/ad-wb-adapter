from pydantic import Field

from schemas.common import BaseOrjsonModel


class ActualStakesAdvertsDTO(BaseOrjsonModel):
    code: str
    advert_id: int = Field(..., alias="advertId")
    id: int
    cpm: int
    subject: int


class SortWaights(BaseOrjsonModel):
    cpm: int
    delivery: int


class ActualStakesDTO(BaseOrjsonModel):
    prioritySubjects: list[int] | None
    adverts: list[ActualStakesAdvertsDTO] | None
    sortWeights: SortWaights | None


class ProductDTO(BaseOrjsonModel):
    id: int
    time1: int | None
    time2: int | None


class ProductsDTO(BaseOrjsonModel):
    products: list[ProductDTO] | None = None


class OrganicDTO(BaseOrjsonModel):
    id: int
    subjectId: int
    time1: int | None = None
    time2: int | None = None


class OrganicsDTO(BaseOrjsonModel):
    products: list[OrganicDTO] | None


class BalanceDTO(BaseOrjsonModel):
    # Счёт, рублей
    balance: int
    # Баланс, рублей
    net: int
    # Бонусы, рублей
    bonus: int | None
