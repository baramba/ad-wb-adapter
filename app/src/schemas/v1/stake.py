from datetime import datetime
from enum import IntEnum, auto

from pydantic import Field

from dto.official.stake import CampaignStatus, CampaignType, IntervalDTO
from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponseSuccess


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


class OperationStatus(IntEnum):
    UPDATED = auto()
    NOT_MODIFIED = auto()
    NOT_UPDATED = auto()


class UpdateCampaignStatus(BaseOrjsonModel):
    status: OperationStatus


class UpdateCampaignResponse(BaseResponseSuccess):
    payload: UpdateCampaignStatus


class Campaign(BaseOrjsonModel):
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
    Begin: int
    End: int


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


class CampaignInfo(Campaign):
    params: list[CampaignParam] | None


class Campaigns(BaseOrjsonModel):
    campaigns: list[Campaign]


class CampaignsResponse(BaseResponseSuccess):
    payload: Campaigns | None


class CampaignResponse(BaseResponseSuccess):
    payload: CampaignInfo | None


class IntervalsRequest(BaseOrjsonModel):
    intervals: list[IntervalDTO]
    param: int | None = None
