import httpx
from adapters.http_adapter import HTTPAdapter
from depends.httpx_client import get_http_client


async def get_http_adapter() -> HTTPAdapter:
    client: httpx.AsyncClient = await get_http_client()
    return HTTPAdapter(client=client)
