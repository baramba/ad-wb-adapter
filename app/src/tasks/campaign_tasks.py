from typing import Any
from adapters.wb.campaign import CampaignAdapter
from arq import ArqRedis
from arq.jobs import Job
from depends.adapters.campaign import get_campaign_adapter
from dto.campaign import CampaignCreateDTO
from utils import depends_decorator


class TaskManager:
    @staticmethod
    async def run_task(arq_poll: ArqRedis, *args: Any, **kwargs: Any) -> int:
        job: Job | None = await arq_poll.enqueue_job(*args, **kwargs)
        if job is None:
            raise Exception("Задача с id=? уже существует.")
        return int(await job.result())


class CampaignTaskManager(TaskManager):
    @classmethod
    async def create_campaign(
        cls, arq_poll: ArqRedis, campaign: CampaignCreateDTO
    ) -> int:
        wb_campaign_id: int = await cls.run_task(
            arq_poll, CampaignTasks.create_campaign.__qualname__, campaign
        )
        return wb_campaign_id

    @classmethod
    async def replenish_budget(
        cls, arq_poll: ArqRedis, wb_campaign_id: int, amount: int
    ) -> None:
        await cls.run_task(
            arq_poll,
            CampaignTasks.replenish_budget.__qualname__,
            wb_campaign_id=wb_campaign_id,
            amount=amount,
        )

    @classmethod
    async def add_keywords_to_campaign(
        cls, arq_poll: ArqRedis, wb_campaign_id: int, keywords: list[str]
    ) -> None:
        await cls.run_task(
            arq_poll,
            CampaignTasks.add_keywords_to_campaign.__qualname__,
            wb_campaign_id=wb_campaign_id,
            keywords=keywords,
        )

    @classmethod
    async def switch_on_fixed_list(
        cls, arq_poll: ArqRedis, wb_campaign_id: int
    ) -> None:
        await cls.run_task(
            arq_poll,
            CampaignTasks.switch_on_fixed_list.__qualname__,
            wb_campaign_id=wb_campaign_id,
        )

    @classmethod
    async def start_campaign(cls, arq_poll: ArqRedis, wb_campaign_id: int) -> None:
        await cls.run_task(
            arq_poll,
            CampaignTasks.switch_on_fixed_list.__qualname__,
            wb_campaign_id=wb_campaign_id,
        )


class CampaignTasks:
    @staticmethod
    @depends_decorator(
        campaign_adapter=get_campaign_adapter,
    )
    async def create_campaign(
        ctx: dict, campaign: CampaignCreateDTO, campaign_adapter: CampaignAdapter
    ) -> int:
        """Создает рекламную кампанию."""
        campaign_id: int = await campaign_adapter.create_campaign(
            name=campaign.name,
            nms=campaign.nms,
        )
        return campaign_id

    @staticmethod
    @depends_decorator(campaign_adapter=get_campaign_adapter)
    async def replenish_budget(
        ctx: dict, wb_campaign_id: int, amount: int, campaign_adapter: CampaignAdapter
    ) -> None:
        """Увеличивает бюджет кампании до заданного значения с округлением в большую сторону."""

        await campaign_adapter.replenish_budget(id=wb_campaign_id, amount=amount)

    @staticmethod
    @depends_decorator(campaign_adapter=get_campaign_adapter)
    async def add_keywords_to_campaign(
        ctx: dict,
        wb_campaign_id: int,
        keywords: list[str],
        campaign_adapter: CampaignAdapter,
    ) -> None:
        """Добавляет ключевые слова в рекламную кампанию."""
        return await campaign_adapter.add_keywords_to_campaign(
            id=wb_campaign_id, keywords=keywords
        )

    @staticmethod
    @depends_decorator(campaign_adapter=get_campaign_adapter)
    async def switch_on_fixed_list(
        ctx: dict,
        wb_campaign_id: int,
        campaign_adapter: CampaignAdapter,
    ) -> None:
        """Включает использование фиксированных фраз в рекламной кампании."""
        await campaign_adapter.switch_on_fixed_list(id=wb_campaign_id)

    @staticmethod
    @depends_decorator(campaign_adapter=get_campaign_adapter)
    async def start_campaign(
        ctx: dict,
        wb_campaign_id: int,
        campaign_adapter: CampaignAdapter,
    ) -> None:
        await campaign_adapter.start_campaign(id=wb_campaign_id)
