from uuid import UUID

from schemas.common import BaseOrjsonModel


class CreateCampaignResponse(BaseOrjsonModel):
    source_id: UUID
    wb_campaign_id: str | None = None
