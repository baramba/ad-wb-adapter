from pydantic import Field
from schemas.common import BaseOrjsonModel
from schemas.v1.base import (
    BaseResponseSuccess,
)


class ActualStakesAdverts(BaseOrjsonModel):
    code: str
    advert_id: int = Field(..., alias="advertId")
    id: int
    cpm: int
    subject: int

    class Config:
        allow_population_by_field_name = True


class ActualStakes(BaseOrjsonModel):
    prioritySubjects: list[int] | None
    adverts: list[ActualStakesAdverts] | None


class StakeResponse(BaseResponseSuccess):
    payload: ActualStakes


class Product(BaseOrjsonModel):
    id: int
    time1: int | None = None
    time2: int | None = None


class Products(BaseOrjsonModel):
    products: list[Product] | None = None


class ProductResponse(BaseResponseSuccess):
    payload: Products


class Organic(BaseOrjsonModel):
    time1: int | None = None
    time2: int | None = None


class OrganicResponse(BaseResponseSuccess):
    payload: Organic
