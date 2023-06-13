from enum import Enum
from uuid import UUID

from dto.official.stake import CampaignType
from schemas.common import BaseOrjsonModel


class CampaignCreateDTO(BaseOrjsonModel):
    name: str
    source_id: UUID
    nms: list[int]
    keywords: list[str]
    budget: int
    type: CampaignType


class Place(BaseOrjsonModel):
    keyWord: str
    subjectId: int
    price: int
    placesInfo: dict
    searchElements: list
    dailyBudget: int
    intervals: list | None = None
    excludedWords: str | None = None


class Budget(BaseOrjsonModel):
    total: int
    dailyMax: int


class CampaignStatus(int, Enum):
    STARTED = 9
    PAUSED = 11


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
