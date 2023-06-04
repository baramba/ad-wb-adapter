import httpx

from adapters.wb.unofficial.campaign import CampaignAdapterUnofficial
from depends.httpx_client import get_http_client


async def get_campaign_adapter_unofficial() -> CampaignAdapterUnofficial:
    client: httpx.AsyncClient = await get_http_client()
    return CampaignAdapterUnofficial(
        http_client=client,
    )
