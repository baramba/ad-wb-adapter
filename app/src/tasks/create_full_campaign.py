import uuid
from http import HTTPStatus

from arq import ArqRedis
from core.settings import settings
from depends.arq import get_arq
from depends.db.redis import get_redis
from depends.services.queue import get_queue_service
from dto.campaign import CreateCampaignDTO
from dto.job_result import RabbitJobResult
from redis.asyncio import Redis
from schemas.v1.base import JobResult
from schemas.v1.campaign import CreateCampaignResponse
from services.queue import BaseQueue
from tasks.campaign_tasks import CampaignTaskManager
from utils import depends_decorator


async def save_and_notify_job_result(
    job_result: str,
    name: str,
    redis: Redis,
    queue_service: BaseQueue,
    routing_key: str,
    message: str,
) -> None:
    await redis.set(
        name=name,
        value=job_result,
        ex=1800,
    )
    await queue_service.publish(queue_name=routing_key, message=message, priority=1)


@depends_decorator(
    redis=get_redis,
    queue_service=get_queue_service,
    arq_poll=get_arq,
)
async def create_full_campaign(
    ctx: dict,
    job_id_: uuid.UUID,
    campaign: CreateCampaignDTO,
    routing_key: str,
    redis: Redis,
    queue_service: BaseQueue,
    arq_poll: ArqRedis,
) -> None:
    wb_campaign_id: int | None = None
    rabbitmq_message = RabbitJobResult(job_id=job_id_).json()
    routing_key = f"{settings.RABBITMQ.SENDER_KEY}.task_complete.{routing_key}"
    job_result: str = ""
    try:
        wb_campaign_id = await CampaignTaskManager.create_campaign(
            arq_poll=arq_poll, campaign=campaign
        )

        await CampaignTaskManager.replenish_budget(
            arq_poll=arq_poll, wb_campaign_id=wb_campaign_id, amount=campaign.budget
        )
        await CampaignTaskManager.add_keywords_to_campaign(
            arq_poll=arq_poll, wb_campaign_id=wb_campaign_id, keywords=campaign.keywords
        )

        await CampaignTaskManager.switch_on_fixed_list(
            arq_poll=arq_poll, wb_campaign_id=wb_campaign_id
        )
        await CampaignTaskManager.start_campaign(
            arq_poll=arq_poll, wb_campaign_id=wb_campaign_id
        )

    except Exception as e:
        job_result = JobResult(
            code=e.__class__.__name__,
            status_code=getattr(e, "status_code", 999),
            text=str(e),
            response=CreateCampaignResponse(source_id=campaign.source_id),
        ).json()
    else:
        job_result = JobResult(
            code="CampaignStartSuccess",
            status_code=HTTPStatus.CREATED,
            response=CreateCampaignResponse(
                wb_campaign_id=str(wb_campaign_id),
                source_id=campaign.source_id,
            ),
        ).json()

    finally:
        await save_and_notify_job_result(
            job_result=job_result,
            name=str(job_id_),
            message=rabbitmq_message,
            routing_key=routing_key,
            redis=redis,
            queue_service=queue_service,
        )
