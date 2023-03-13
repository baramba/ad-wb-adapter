import uuid

from redis.asyncio import Redis

from adapters.campaign import CampaignAdapter
from depends.adapters.campaign import get_campaign_adapter
from depends.db.redis import get_redis
from dto.campaign import CreateCampaignDTO
from schemas.v1.campaign import CreateCampaignResponse
from utils import depends_decorator


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
    redis=get_redis,
)
async def create_campaign(
        ctx,
        job_id_: uuid.UUID,
        campaign: CreateCampaignDTO,
        campaign_adapter: CampaignAdapter = None,
        redis: Redis = None,
):
    print(type(redis),flush=True)
    campaign_id = await campaign_adapter.create_campaign(
        **campaign.dict()
    )

    await redis.set(
        name=str(job_id_),
        value=CreateCampaignResponse(id=campaign_id).json(),
        ex=1800
    )
