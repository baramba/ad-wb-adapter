import enum

from pydantic import BaseModel


class CampaignTypeEnum(str, enum.Enum):
    search = 'search'


class CreateCampaignDTO(BaseModel):
    name: str
    nms: list[int]
    keywords: list[str]
    budget: int
    type: CampaignTypeEnum
