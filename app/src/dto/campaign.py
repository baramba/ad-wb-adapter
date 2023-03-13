from pydantic import BaseModel


class CreateCampaignDTO(BaseModel):
    name: str
    nms: list[int]
