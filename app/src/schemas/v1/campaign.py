from pydantic import BaseModel


class CreateCampaignResponse(BaseModel):
    id: str
