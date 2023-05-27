from fastapi import Depends
import httpx
from adapters.wb.supplier import SupplierAdapter
from depends.httpx_client import get_http_client


async def get_supplier_adapter(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> SupplierAdapter:
    return SupplierAdapter(client=client)
