import asyncio
import uuid

from arq import Retry
from httpx import HTTPError
from redis.asyncio import Redis

from adapters.campaign import CampaignAdapter
from depends.adapters.campaign import get_campaign_adapter
from depends.db.redis import get_redis
from depends.services.queue import get_queue_service
from dto.campaign import CreateCampaignDTO
from dto.job_result import RabbitJobResult
from exceptions.campaign import CampaignError
from schemas.v1.base import JobResult
from schemas.v1.campaign import CreateCampaignResponse
from services.queue import BaseQueue
from utils import depends_decorator


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
    redis=get_redis,
    queue_service=get_queue_service
)
async def create_full_campaign(
        ctx,
        job_id_: uuid.UUID,
        campaign: CreateCampaignDTO,
        routing_key: str,
        campaign_adapter: CampaignAdapter = None,
        redis: Redis = None,
        queue_service: BaseQueue = None,
):
    campaign_id = None
    rabbitmq_message = RabbitJobResult(job_id=job_id_).json()
    routing_key = f"{routing_key}:task_complete"
    try:
        campaign_id = await campaign_adapter.create_campaign(
            name=campaign.name,
            nms=campaign.nms,
        )
        await campaign_adapter.add_amount_to_campaign_budget(
            id=campaign_id,
            amount=campaign.budget)
        budget = await campaign_adapter.set_campaign_bet(
            id=campaign_id,
            bet=campaign.budget)
        await campaign_adapter.add_keywords_to_campaign(
            id=campaign_id,
            keywords=campaign.keywords
        )
        await asyncio.sleep(3)
        await campaign_adapter.start_campaign(
            id=campaign_id,
            budget=budget
        )
    except Exception as e:
        if campaign_id is None:
            value = JobResult(
                code=e.__class__.__name__,
                status_code=getattr(e, 'status_code', 999),
                text=str(e),
                response={}
            ).json()
        else:
            value = JobResult(
                code=e.__class__.__name__,
                status_code=getattr(e, 'status_code', 999),
                text=str(e),
                response=CreateCampaignResponse(id=campaign_id)
            ).json()

        await redis.set(
            name=str(job_id_),
            value=value,
            ex=1800,
        )
        await queue_service.publish(queue_name=routing_key,
                                    message=rabbitmq_message,
                                    priority=1)

        if campaign_id is None:
            raise Retry(defer=30)

        return

    await redis.set(
        name=str(job_id_),
        value=JobResult(
            code='CampaignStartSuccess',
            status_code=201,
            response=CreateCampaignResponse(id=campaign_id)
        ).json(),
        ex=1800
    )
    await queue_service.publish(queue_name=routing_key,
                                message=rabbitmq_message,
                                priority=1)
