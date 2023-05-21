import uuid
from fastapi import Depends
from adapters.token_manager import TokenManager
from adapters.wb.campaign import CampaignAdapter
from adapters.wb.stake import StakeAdapter
from depends.adapters.campaign import get_campaign_adapter
from depends.adapters.stake import get_stake_adapter
from depends.adapters.token import get_token_manager_adapter
from dto.campaign import CampaignConfigDTO, CampaignStatus
from dto.stake import ActualStakesDTO, OrganicDTO, ProductsDTO
from schemas.v1.stake import OperationStatus


class StakeService:
    def __init__(
        self,
        stake_adapter: StakeAdapter,
        campaign_adapter: CampaignAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.stake_adapter = stake_adapter
        self.campaign_adapter = campaign_adapter
        self.token_manager = token_manager

    async def actual_stakes(
        self,
        keyword: str,
    ) -> ActualStakesDTO:
        return await self.stake_adapter.actual_stakes(keyword=keyword)

    async def products_by_region(
        self,
        dest: str,
        nm: str,
    ) -> ProductsDTO:
        return await self.stake_adapter.products_by_region(dest=dest, nm=nm)

    async def organic_by_region(
        self,
        dest: str,
        query: str,
        resultset: str,
    ) -> OrganicDTO:
        return await self.stake_adapter.organic_by_region(
            dest=dest, query=query, resultset=resultset
        )

    async def set_new_rate(
        self,
        wb_campaign_id: int,
        rate: int,
        user_id: uuid.UUID,
    ) -> bool:
        self.campaign_adapter.auth_data = await self.token_manager.auth_data_by_user_id(
            user_id
        )
        config: CampaignConfigDTO = await self.campaign_adapter.get_campaign_config(
            id=wb_campaign_id
        )
        config.place[0].price = rate

        await self.campaign_adapter.update_campaign_rate(
            id=wb_campaign_id, config=config
        )
        return True

    async def pause_campaign(
        self,
        wb_campaign_id: int,
        user_id: uuid.UUID,
    ) -> CampaignStatus:
        self.campaign_adapter.auth_data = await self.token_manager.auth_data_by_user_id(
            user_id
        )

        return await self.campaign_adapter.pause_campaign(id=wb_campaign_id)

    async def resume_campaign(
        self,
        wb_campaign_id: int,
        user_id: uuid.UUID,
    ) -> OperationStatus:
        self.campaign_adapter.auth_data = await self.token_manager.auth_data_by_user_id(
            user_id
        )
        config: CampaignConfigDTO = await self.campaign_adapter.get_campaign_config(
            id=wb_campaign_id
        )
        # если config.budget.total, то wb возвращает ошибку "Для запуска/возобновления показов пополните бюджет кампании"
        config.budget.total = 100
        if config.status == CampaignStatus.STARTED:
            return OperationStatus.NOT_MODIFIED

        config.status = CampaignStatus.STARTED
        await self.campaign_adapter.update_campaign_config(
            id=wb_campaign_id, config=config
        )
        return OperationStatus.UPDATED


async def get_stake_service(
    stake_adapter: StakeAdapter = Depends(get_stake_adapter),
    campaign_adapter: CampaignAdapter = Depends(get_campaign_adapter),
    token_manager: TokenManager = Depends(get_token_manager_adapter),
) -> StakeService:
    return StakeService(
        stake_adapter=stake_adapter,
        campaign_adapter=campaign_adapter,
        token_manager=token_manager,
    )
