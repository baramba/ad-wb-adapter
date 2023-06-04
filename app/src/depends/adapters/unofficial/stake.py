import httpx

from adapters.wb.unofficial.stake import StakeAdapterUnofficial
from depends.httpx_client import get_http_client


async def get_stake_adapter_unofficial() -> StakeAdapterUnofficial:
    client: httpx.AsyncClient = await get_http_client()
    return StakeAdapterUnofficial(http_client=client)
