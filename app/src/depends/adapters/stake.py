from adapters.http_adapter import HTTPAdapter
from adapters.wb.stake import StakeAdapter
from depends.adapters.http_adapter import get_http_adapter


async def get_stake_adapter() -> StakeAdapter:
    client: HTTPAdapter = await get_http_adapter()
    return StakeAdapter(client=client)
