import uuid

from fastapi import Depends

from adapters.wb.official.stake import StakeAdapter
from adapters.wb.unofficial.supplier import SupplierAdapter
from depends.adapters.official.stake import get_stake_adapter
from depends.adapters.unofficial.supplier import get_supplier_adapter_un
from dto.unofficial.stake import BalanceDTO


class SupplierService:
    def __init__(self, supplier_adapter: SupplierAdapter, stake_adapter: StakeAdapter) -> None:
        self.supplier_adapter = supplier_adapter
        self.stake_adapter = stake_adapter

    async def get_auth_wb_user(
        self,
        wb_token_refresh: str,
        wb_x_supplier_id_external: uuid.UUID,
    ) -> str:
        wb_token_access: str = await self.supplier_adapter.wb_user_auth(wb_token_refresh, wb_x_supplier_id_external)
        return wb_token_access

    async def balance(self) -> BalanceDTO:
        return await self.stake_adapter.balance()


async def get_supplier_service(
    supplier_adapter: SupplierAdapter = Depends(get_supplier_adapter_un),
    stake_adapter: StakeAdapter = Depends(get_stake_adapter),
) -> SupplierService:
    return SupplierService(supplier_adapter=supplier_adapter, stake_adapter=stake_adapter)
