from uuid import UUID

from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponseSuccess


class CreateCampaignResponse(BaseOrjsonModel):
    source_id: UUID
    wb_campaign_id: str | None = None


class Budget(BaseOrjsonModel):
    amount: int


class ReplenishBugetResponse(BaseResponseSuccess):
    payload: Budget
