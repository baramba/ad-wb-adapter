from pydantic import Field

from schemas.common import BaseOrjsonModel


class ActualStakesAdvertsDTO(BaseOrjsonModel):
    code: str
    advert_id: int = Field(..., alias="advertId")
    id: int
    cpm: int
    subject: int


class ActualStakesDTO(BaseOrjsonModel):
    prioritySubjects: list[int] | None
    adverts: list[ActualStakesAdvertsDTO] | None


class ProductDTO(BaseOrjsonModel):
    id: int
    time1: int | None
    time2: int | None


class ProductsDTO(BaseOrjsonModel):
    products: list[ProductDTO] | None = None


class OrganicDTO(BaseOrjsonModel):
    time1: int | None = None
    time2: int | None = None
