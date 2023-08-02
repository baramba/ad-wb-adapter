import uuid

from fastapi import Depends

from adapters.token import TokenManager
from adapters.wb.official.advert import AdvertAdapter
from adapters.wb.unofficial.supplier import SupplierAdapter
from core.utils.context import AppContext
from depends.adapters.official.advert import get_advert_adapter
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.supplier import get_supplier_adapter_un
from dto.official.advert import BalanceDTO


class SupplierService:
    def __init__(
        self,
        supplier_adapter: SupplierAdapter,
        advert_adapter: AdvertAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.supplier_adapter = supplier_adapter
        self.advert_adapter = advert_adapter
        self.token_manager = token_manager

    async def get_auth_wb_user(
        self,
        wb_token_refresh: str,
        wb_x_supplier_id_external: uuid.UUID,
    ) -> str:
        wb_token_access: str = await self.supplier_adapter.wb_user_auth(wb_token_refresh, wb_x_supplier_id_external)
        return wb_token_access

    async def balance(self) -> BalanceDTO:
        auth_data = await self.token_manager.auth_data_by_user_id_official(AppContext.user_id())
        self.advert_adapter.auth_data = auth_data
        return await self.advert_adapter.balance()


async def get_supplier_service(
    supplier_adapter: SupplierAdapter = Depends(get_supplier_adapter_un),
    advert_adapter: AdvertAdapter = Depends(get_advert_adapter),
    token_manager: TokenManager = Depends(get_token_manager),
) -> SupplierService:
    return SupplierService(
        supplier_adapter=supplier_adapter, advert_adapter=advert_adapter, token_manager=token_manager
    )
