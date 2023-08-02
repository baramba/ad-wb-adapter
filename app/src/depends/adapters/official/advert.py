import httpx

from adapters.wb.official.advert import AdvertAdapter
from depends.httpx_client import get_http_client


async def get_advert_adapter() -> AdvertAdapter:
    client: httpx.AsyncClient = await get_http_client()
    return AdvertAdapter(http_client=client)
