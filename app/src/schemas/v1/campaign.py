from uuid import UUID

from pydantic import BaseModel


class CreateCampaignResponse(BaseModel):
    wb_campaign_id: str | None = None
    source_id: UUID
