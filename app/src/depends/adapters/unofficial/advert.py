import httpx

from adapters.wb.unofficial.advert import AdvertAdapterUnofficial
from depends.httpx_client import get_http_client


async def get_stake_adapter_unofficial() -> AdvertAdapterUnofficial:
    client: httpx.AsyncClient = await get_http_client()
    return AdvertAdapterUnofficial(http_client=client)
