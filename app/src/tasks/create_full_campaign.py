import asyncio
import uuid
from http import HTTPStatus

from redis.asyncio import Redis

from adapters.token import TokenManager
from adapters.wb.unofficial.campaign import CampaignAdapterUnofficial
from core.settings import logger, settings
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.campaign import get_campaign_adapter_unofficial
from depends.db.redis import get_redis
from depends.services.queue import get_queue_service
from dto.job_result import RabbitJobResult
from dto.token import WbUserAuthDataDTO
from dto.unofficial.campaign import CampaignCreateDTO
from exceptions.base import WBAErrorNotAuth
from schemas.v1.base import JobResult
from schemas.v1.campaign import CreateCampaignResponse
from services.queue import BaseQueue
from utils import depends_decorator


class CampaignCreateFullTask:
    @classmethod
    @depends_decorator(
        redis=get_redis,
        queue_service=get_queue_service,
        campaign_adapter=get_campaign_adapter_unofficial,
        token_manager=get_token_manager,
    )
    async def create_full_campaign(
        cls,
        ctx: dict,
        job_id: uuid.UUID,
        campaign: CampaignCreateDTO,
        routing_key: str,
        user_id: uuid.UUID,
        redis: Redis,
        queue_service: BaseQueue,
        campaign_adapter: CampaignAdapterUnofficial,
        token_manager: TokenManager,
    ) -> None:
        rabbitmq_message = RabbitJobResult(job_id=job_id).json()
        job_result: str = ""

        user_auth_data: WbUserAuthDataDTO = await token_manager.auth_data_by_user_id(user_id)

        campaign_adapter.auth_data = user_auth_data

        try:
            wb_campaign_id = await campaign_adapter.create_campaign(
                name=campaign.name,
                nms=campaign.nms,
            )
        except WBAErrorNotAuth:
            await token_manager.request_update_user_access_token(
                user_id=user_id, wb_token_access=user_auth_data.wb_token_access
            )

        await asyncio.sleep(10)
        user_auth_data = await token_manager.auth_data_by_user_id(user_id)
        campaign_adapter.auth_data = user_auth_data
        wb_campaign_id = await campaign_adapter.create_campaign(
            name=campaign.name,
            nms=campaign.nms,
        )

        try:
            await campaign_adapter.replenish_budget(id=wb_campaign_id, amount=campaign.budget)
            await campaign_adapter.add_keywords_to_campaign(id=wb_campaign_id, keywords=campaign.keywords)
            await campaign_adapter.switch_on_fixed_list(id=wb_campaign_id)
            await campaign_adapter.start_campaign(id=wb_campaign_id)

        except Exception as e:
            logger.exception(e)
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
            ex=settings.REDIS.JOB_RESULT_EX_TIME,
        )
        await queue_service.publish(routing_key=routing_key, message=message, priority=1)
