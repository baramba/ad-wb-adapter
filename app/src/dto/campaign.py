import enum
from uuid import UUID
from schemas.common import BaseOrjsonModel


class CampaignTypeEnum(str, enum.Enum):
    search = "search"


class CreateCampaignDTO(BaseOrjsonModel):
    name: str
    source_id: UUID
    nms: list[int]
    keywords: list[str]
    budget: int
    type: CampaignTypeEnum


class Place(BaseOrjsonModel):
    keyWord: str
    subjectId: int
    price: int
    placesInfo: dict
    searchElements: list
    dailyBudget: int
    intervals: str | None = None
    excludedWords: str | None = None


class Budget(BaseOrjsonModel):
    total: int
    dailyMax: int


class CampaignConfigDTO(BaseOrjsonModel):
    budget: Budget
    minCPM: int
    stepCPM: int
    locale: list[int]
    place: list[Place]
    limited: bool
    nmsCount: int
    name: str
    status: int
    fixed: bool
