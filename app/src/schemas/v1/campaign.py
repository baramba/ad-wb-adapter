from uuid import UUID

from pydantic import Field

from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponseSuccess


class CreateCampaignResponse(BaseOrjsonModel):
    source_id: UUID
    wb_campaign_id: str | None = None


class Budget(BaseOrjsonModel):
    budget: int = Field(description="Текущий бюджет рекламной кампании")


class ReplenishBugetResponse(BaseResponseSuccess):
    payload: Budget
