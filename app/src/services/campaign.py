from fastapi import Depends

from adapters.token import TokenManager
from adapters.wb.official.advert import AdvertAdapter
from adapters.wb.unofficial.campaign import CampaignAdapterUnofficial
from core.utils.context import AppContext
from depends.adapters.official.advert import get_advert_adapter
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.campaign import get_campaign_adapter_unofficial
from dto.official.advert import BudgetDTO, CampaignInfoDTO, CampaignsDTO, CampaignStatus, CampaignType
from dto.token import OfficialUserAuthDataDTO
from dto.unofficial.campaign import ReplenishBugetRequestDTO


class CampaignService:
    def __init__(
        self,
        campaign_adapter_unofficial: CampaignAdapterUnofficial,
        advert_adapter: AdvertAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.advert_adapter = advert_adapter
        self.campaign_adapter_unofficial = campaign_adapter_unofficial
        self.token_manager = token_manager

    async def replenihs_budget(self, replenish: ReplenishBugetRequestDTO) -> int:
        """Метод ползволяет пополнить бюджет кампании на X рублей.

        Returns:
            Возвращает новое значение бюджета кампании.
        """
        auth_data = await self.token_manager.auth_data_by_user_id_unofficial(AppContext.user_id())
        self.campaign_adapter_unofficial.auth_data = auth_data
        self.advert_adapter.auth_data = OfficialUserAuthDataDTO(wb_token_ad=auth_data.wb_token_ad)
        await self.campaign_adapter_unofficial.replenish_budget_at(replenish)
        amount = await self.campaign_adapter_unofficial.get_campaign_budget(id=replenish.wb_campaign_id)
        return int(amount)

    async def campaigns(
        self,
        type: CampaignType | None,
        status: CampaignStatus | None,
        limit: int | None = None,
    ) -> CampaignsDTO | None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(AppContext.user_id())
        self.advert_adapter.auth_data = auth_data
        return await self.advert_adapter.campaigns(type=type, status=status, limit=limit)

    async def campaign(self, campaign_id: int) -> CampaignInfoDTO | None:
        auth_data = await self.token_manager.auth_data_by_user_id_official(AppContext.user_id())
        self.advert_adapter.auth_data = auth_data
        return await self.advert_adapter.campaign(id=campaign_id)

    async def budget(self, wb_campaign_id: int) -> BudgetDTO:
        auth_data = await self.token_manager.auth_data_by_user_id_official(AppContext.user_id())
        self.advert_adapter.auth_data = auth_data
        return await self.advert_adapter.budget(wb_campaign_id=wb_campaign_id)


async def get_campaign_service(
    campaign_adapter_unofficial: CampaignAdapterUnofficial = Depends(get_campaign_adapter_unofficial),
    advert_adapter: AdvertAdapter = Depends(get_advert_adapter),
    token_manager: TokenManager = Depends(get_token_manager),
) -> CampaignService:
    return CampaignService(
        advert_adapter=advert_adapter,
        campaign_adapter_unofficial=campaign_adapter_unofficial,
        token_manager=token_manager,
    )
