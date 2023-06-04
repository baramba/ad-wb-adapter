import httpx

from adapters.wb.unofficial.product import ProductAdapter
from depends.httpx_client import get_http_client


async def get_product_adapter_un() -> ProductAdapter:
    client: httpx.AsyncClient = await get_http_client()
    return ProductAdapter(http_client=client)
