import uuid

from fastapi import Depends

from adapters.token import TokenManager
from adapters.wb.official.advert import AdvertAdapter
from adapters.wb.unofficial.advert import AdvertAdapterUnofficial
from adapters.wb.unofficial.campaign import CampaignAdapterUnofficial
from core.settings import logger
from depends.adapters.official.advert import get_advert_adapter
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.advert import get_stake_adapter_unofficial
from depends.adapters.unofficial.campaign import get_campaign_adapter_unofficial
from dto.official.advert import IntervalDTO
from dto.unofficial.advert import ActualStakesDTO, OrganicsDTO, ProductsDTO


class AdvertService:
    def __init__(
        self,
        advert_adapter_unofficial: AdvertAdapterUnofficial,
        campaign_adapter_unofficial: CampaignAdapterUnofficial,
        advert_adapter: AdvertAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.stake_adapter = advert_adapter
        self.campaign_adapter_unofficial = campaign_adapter_unofficial
        self.advert_adapter_unofficial = advert_adapter_unofficial
        self.token_manager = token_manager

    async def actual_stakes(
        self,
        keyword: str,
    ) -> ActualStakesDTO:
        return await self.advert_adapter_unofficial.actual_stakes(keyword=keyword)

    async def products_by_region(
        self,
        dest: str,
        nm: str,
    ) -> ProductsDTO:
        return await self.advert_adapter_unofficial.products_by_region(dest=dest, nm=nm)

    async def organic_by_region(
        self,
        dest: str,
        query: str,
        resultset: str,
    ) -> OrganicsDTO:
        return await self.advert_adapter_unofficial.organic_by_region(dest=dest, query=query, resultset=resultset)

    async def set_new_rate(
        self,
        wb_campaign_id: int,
        rate: int,
        user_id: uuid.UUID,
        ad_type: int,
        param: int | None = None,
    ) -> None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(user_id)
        self.stake_adapter.auth_data = auth_data

        # TODO: убрать после добавления subject_id в доменную модель campaign manager
        if param:
            await self.stake_adapter.change_rate(advert_id=wb_campaign_id, cpm=rate, param=param, type=ad_type)
        elif campaign := await self.stake_adapter.campaign(id=wb_campaign_id):
            if campaign.params and campaign.params[0].subjectId:
                subject_id = campaign.params[0].subjectId
                param = subject_id
        if not param:
            logger.error(f"Could not get subject_id. wb_campaign_id={wb_campaign_id}")
            return

        await self.stake_adapter.change_rate(advert_id=wb_campaign_id, cpm=rate, param=param, type=ad_type)

    async def pause_campaign(
        self,
        wb_campaign_id: int,
        user_id: uuid.UUID,
    ) -> None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(user_id)
        self.stake_adapter.auth_data = auth_data
        await self.stake_adapter.pause_campaign(id=wb_campaign_id)

    async def resume_campaign(
        self,
        wb_campaign_id: int,
        user_id: uuid.UUID,
    ) -> None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(user_id)
        self.stake_adapter.auth_data = auth_data
        await self.stake_adapter.start_campaign(id=wb_campaign_id)

    async def set_time_intervals(
        self,
        user_id: uuid.UUID,
        wb_campaign_id: int,
        intervals: list[IntervalDTO],
        param: int | None,
    ) -> None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(user_id)
        self.stake_adapter.auth_data = auth_data

        # TODO: убрать после добавления subject_id в доменную модель campaign manager
        if param:
            await self.stake_adapter.set_time_intervals(wb_campaign_id=wb_campaign_id, intervals=intervals, param=param)
        elif campaign := await self.stake_adapter.campaign(id=wb_campaign_id):
            if campaign.params and campaign.params[0].subjectId:
                subject_id = campaign.params[0].subjectId
                param = subject_id
        if not param:
            logger.error(f"Не удалось получить subject_id. wb_campaign_id={wb_campaign_id}")
            return

        await self.stake_adapter.set_time_intervals(wb_campaign_id=wb_campaign_id, intervals=intervals, param=param)


async def get_stake_service(
    stake_adapter_unofficial: AdvertAdapterUnofficial = Depends(get_stake_adapter_unofficial),
    campaign_adapter_unofficial: CampaignAdapterUnofficial = Depends(get_campaign_adapter_unofficial),
    stake_adapter: AdvertAdapter = Depends(get_advert_adapter),
    token_manager: TokenManager = Depends(get_token_manager),
) -> AdvertService:
    return AdvertService(
        advert_adapter_unofficial=stake_adapter_unofficial,
        advert_adapter=stake_adapter,
        campaign_adapter_unofficial=campaign_adapter_unofficial,
        token_manager=token_manager,
    )
