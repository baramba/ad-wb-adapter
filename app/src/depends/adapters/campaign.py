from adapters.wb.campaign import CampaignAdapter
from depends.adapters.http_adapter import get_http_adapter


async def get_campaign_adapter() -> CampaignAdapter:
    return CampaignAdapter(
        client=await get_http_adapter(),
    )
