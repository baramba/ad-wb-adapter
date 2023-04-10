import enum
from uuid import UUID

from pydantic import BaseModel


class CampaignTypeEnum(str, enum.Enum):
    search = "search"


class CreateCampaignDTO(BaseModel):
    name: str
    source_id: UUID
    nms: list[int]
    keywords: list[str]
    budget: int
    type: CampaignTypeEnum
