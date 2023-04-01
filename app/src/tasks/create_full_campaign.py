import math
import uuid

from arq import Retry, ArqRedis
from redis.asyncio import Redis

from adapters.campaign import CampaignAdapter
from core.settings import settings
from depends.adapters.campaign import get_campaign_adapter
from depends.arq import get_arq
from depends.db.redis import get_redis
from depends.services.queue import get_queue_service
from dto.campaign import CreateCampaignDTO
from dto.job_result import RabbitJobResult
from schemas.v1.base import JobResult
from schemas.v1.campaign import CreateCampaignResponse
from services.queue import BaseQueue
from utils import depends_decorator, run_kinda_async_task, retry_


@depends_decorator(
    redis=get_redis,
    queue_service=get_queue_service,
    arq_poll=get_arq,
)
async def create_full_campaign(
        ctx,
        job_id_: uuid.UUID,
        campaign: CreateCampaignDTO,
        routing_key: str,
        redis: Redis = None,
        queue_service: BaseQueue = None,
        arq_poll: ArqRedis = None,
):
    campaign_id = None
    rabbitmq_message = RabbitJobResult(job_id=job_id_).json()
    routing_key = f"{settings.RABBITMQ.SENDER_KEY}.task_complete.{routing_key}"
    try:
        campaign_id = await run_kinda_async_task(
            arq_poll,
            '_create_campaign',
            campaign
        )

        campaign = await run_kinda_async_task(
            arq_poll,
            '_add_amount_to_campaign_budget',
            campaign_id,
            campaign
        )

        budget = await run_kinda_async_task(
            arq_poll,
            '_set_campaign_bet',
            campaign_id,
            campaign
        )

        await run_kinda_async_task(
            arq_poll,
            '_add_keywords_to_campaign',
            campaign_id,
            campaign
        )

        await run_kinda_async_task(
            arq_poll,
            '_add_keywords_to_campaign',
            campaign_id,
            campaign
        )

        await run_kinda_async_task(
            arq_poll,
            '_start_campaign',
            campaign_id,
            budget
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


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
)
@retry_()
async def _create_campaign(
        ctx,
        campaign: CreateCampaignDTO,
        campaign_adapter: CampaignAdapter = None,
):
    campaign_id = await campaign_adapter.create_campaign(
        name=campaign.name,
        nms=campaign.nms,
    )
    return campaign_id


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
)
@retry_()
async def _add_amount_to_campaign_budget(
        ctx,
        campaign_id: int,
        campaign: CreateCampaignDTO,
        campaign_adapter: CampaignAdapter = None,
):
    current_budget = await campaign_adapter.get_campaign_budget(id=campaign_id)
    current_budget = current_budget["budget"]["total"]
    if current_budget >= campaign.budget:
        return
    if current_budget != 0:
        campaign.budget = max(100, math.ceil(current_budget / 50) * 50)
    await campaign_adapter.add_amount_to_campaign_budget(
        id=campaign_id,
        amount=campaign.budget
    )
    return campaign


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
)
@retry_()
async def _set_campaign_bet(
        ctx,
        campaign_id: int,
        campaign: CreateCampaignDTO,
        campaign_adapter: CampaignAdapter = None,
) -> dict:
    return await campaign_adapter.set_campaign_bet(
        id=campaign_id,
        bet=campaign.budget)


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
)
@retry_()
async def _add_keywords_to_campaign(
        ctx,
        campaign_id: int,
        campaign: CreateCampaignDTO,
        campaign_adapter: CampaignAdapter = None,
):
    return await campaign_adapter.add_keywords_to_campaign(
        id=campaign_id,
        keywords=campaign.keywords
    )


@depends_decorator(
    campaign_adapter=get_campaign_adapter,
)
@retry_()
async def _start_campaign(
        ctx,
        campaign_id: int,
        budget: dict,
        campaign_adapter: CampaignAdapter = None,
):
    return await campaign_adapter.start_campaign(
        id=campaign_id,
        budget=budget
    )


private_tasks = [
    _create_campaign,
    _add_amount_to_campaign_budget,
    _set_campaign_bet,
    _add_keywords_to_campaign,
    _start_campaign,
]
