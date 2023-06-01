import httpx
from fastapi import Depends

from adapters.wb.unofficial.supplier import SupplierAdapter
from depends.httpx_client import get_http_client


async def get_supplier_adapter_un(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> SupplierAdapter:
    return SupplierAdapter(http_client=client)
