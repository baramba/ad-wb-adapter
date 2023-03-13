from adapters.campaign import CampaignAdapter
from core.settings import settings
from depends.httpx_client import get_client


async def get_campaign_adapter() -> CampaignAdapter:
    return CampaignAdapter(
        client=await get_client(),
        supplier_id=settings.WILDBERRIES.X_SUPPLIER_ID,
        supplier_id_external=settings.WILDBERRIES.X_SUPPLIER_ID_EXTERNAl,
        user_id=settings.WILDBERRIES.X_USER_ID,
        wb_token=settings.WILDBERRIES.WB_TOKEN,
    )
