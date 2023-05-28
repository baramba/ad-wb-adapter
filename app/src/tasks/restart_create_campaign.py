from http import HTTPStatus
import uuid
from redis.asyncio import Redis
from adapters.wb.campaign import CampaignAdapter
from adapters.token_manager import TokenManager
from depends.adapters.campaign import get_campaign_adapter
from depends.adapters.token import get_token_manager_adapter
from depends.db.redis import get_redis
from depends.services.queue import get_queue_service
from dto.campaign import CampaignCreateDTO
from dto.job_result import RabbitJobResult
from schemas.v1.base import JobResult
from schemas.v1.campaign import CreateCampaignResponse
from dto.supplier import WbUserAuthDataDTO
from services.queue import BaseQueue
from utils import depends_decorator


class CampaignCreateFullTask:
    @classmethod
    @depends_decorator(
        redis=get_redis,
        queue_service=get_queue_service,
        campaign_adapter=get_campaign_adapter,
        token_manager=get_token_manager_adapter,
    )
    async def restart_create_full_campaign(
        cls,
        ctx: dict,
        job_id: uuid.UUID,
        campaign: CampaignCreateDTO,
        routing_key: str,
        user_id: uuid.UUID,
        redis: Redis,
        queue_service: BaseQueue,
        campaign_adapter: CampaignAdapter,
        token_manager: TokenManager,
    ) -> None:
        rabbitmq_message = RabbitJobResult(job_id=job_id).json()
        job_result: str = ""

        user_auth_data: WbUserAuthDataDTO = await token_manager.auth_data_by_user_id(
            user_id
        )

        campaign_adapter.auth_data = user_auth_data

        try:
            wb_campaign_id = await campaign_adapter.create_campaign(
                name=campaign.name,
                nms=campaign.nms,
            )
            await campaign_adapter.replenish_budget(
                id=wb_campaign_id, amount=campaign.budget
            )
            await campaign_adapter.add_keywords_to_campaign(
                id=wb_campaign_id, keywords=campaign.keywords
            )
            await campaign_adapter.switch_on_fixed_list(id=wb_campaign_id)
            await campaign_adapter.start_campaign(id=wb_campaign_id)

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
            await cls.save_and_notify_job_result(
                job_result=job_result,
                name=str(job_id),
                message=rabbitmq_message,
                routing_key=routing_key,
                redis=redis,
                queue_service=queue_service,
            )

    @classmethod
    @depends_decorator(
        redis=get_redis,
        queue_service=get_queue_service,
        campaign_adapter=get_campaign_adapter,
        token_manager=get_token_manager_adapter,
    )
    async def save_and_notify_job_result(
        cls,
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
        await queue_service.publish(
            routing_key=routing_key, message=message, priority=1
        )
