from uuid import UUID

from schemas.common import BaseOrjsonModel


class CreateCampaignResponse(BaseOrjsonModel):
    wb_campaign_id: str | None = None
    source_id: UUID
