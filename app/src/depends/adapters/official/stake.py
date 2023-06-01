import httpx

from adapters.wb.official.stake import StakeAdapter
from depends.httpx_client import get_http_client


async def get_stake_adapter() -> StakeAdapter:
    client: httpx.AsyncClient = await get_http_client()
    return StakeAdapter(http_client=client)
