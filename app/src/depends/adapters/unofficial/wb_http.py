import httpx

from adapters.wb.unofficial.wbadapter import WBAdapterUnofficial
from depends.httpx_client import get_http_client


async def get_wb_http_adapter_un() -> WBAdapterUnofficial:
    client: httpx.AsyncClient = await get_http_client()
    return WBAdapterUnofficial(http_client=client)
