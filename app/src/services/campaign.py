from fastapi import Depends

from adapters.token import TokenManager
from adapters.wb.official.stake import StakeAdapter
from adapters.wb.unofficial.campaign import CampaignAdapterUnofficial
from core.utils.context import AppContext
from depends.adapters.official.stake import get_stake_adapter
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.campaign import get_campaign_adapter_unofficial
from dto.token import OfficialUserAuthDataDTO
from dto.unofficial.campaign import ReplenishBugetRequestDTO


class CampaignService:
    def __init__(
        self,
        campaign_adapter_unofficial: CampaignAdapterUnofficial,
        stake_adapter: StakeAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.stake_adapter = stake_adapter
        self.campaign_adapter_unofficial = campaign_adapter_unofficial
        self.token_manager = token_manager

    async def replenihs_budget(self, replenish: ReplenishBugetRequestDTO) -> int:
        """Метод ползволяет пополнить бюджет кампании на X рублей.

        Returns:
            Возвращает новое значение бюджета кампании.
        """
        auth_data = await self.token_manager.auth_data_by_user_id_unofficial(AppContext.user_id())
        self.campaign_adapter_unofficial.auth_data = auth_data
        self.stake_adapter.auth_data = OfficialUserAuthDataDTO(wb_token_ad=auth_data.wb_token_ad)
        await self.campaign_adapter_unofficial.replenish_budget_at(replenish)
        amount = await self.campaign_adapter_unofficial.get_campaign_budget(id=replenish.wb_campaign_id)
        return int(amount)


async def get_campaign_service(
    campaign_adapter_unofficial: CampaignAdapterUnofficial = Depends(get_campaign_adapter_unofficial),
    stake_adapter: StakeAdapter = Depends(get_stake_adapter),
    token_manager: TokenManager = Depends(get_token_manager),
) -> CampaignService:
    return CampaignService(
        stake_adapter=stake_adapter,
        campaign_adapter_unofficial=campaign_adapter_unofficial,
        token_manager=token_manager,
    )
