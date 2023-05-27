import uuid
from fastapi import Depends
from adapters.wb.supplier import SupplierAdapter
from depends.adapters.supplier import get_supplier_adapter


class SupplierService:
    def __init__(self, supplier_adapter: SupplierAdapter) -> None:
        self.supplier_adapter = supplier_adapter

    async def get_auth_wb_user(
        self,
        wb_token_refresh: str,
        wb_x_supplier_id_external: uuid.UUID,
    ) -> str:
        wb_token_access: str = await self.supplier_adapter.wb_user_auth(
            wb_token_refresh, wb_x_supplier_id_external
        )
        return wb_token_access


async def get_supplier_service(
    supplier_adapter: SupplierAdapter = Depends(get_supplier_adapter),
) -> SupplierService:
    return SupplierService(supplier_adapter=supplier_adapter)
