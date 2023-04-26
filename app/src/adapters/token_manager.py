import uuid
from adapters.http_adapter import HTTPAdapter
from core.settings import settings
from schemas.v1.supplier import WbUserAuthData


class TokenManager:
    def __init__(self, client: HTTPAdapter) -> None:
        self.url = settings.TOKEN_MANAGER_URL
        self.client = client

    async def auth_data_by_user_id(self, user_id: uuid.UUID) -> WbUserAuthData:
        url = f"{self.url}/auth_data"
        params = {"user_id": user_id}

        response = await self.client._get(url=url, params=params)
        result = response.json()
        wb_user_id = result["wb_user_id"]
        wb_supplier_id = result["wb_supplier_id"]
        wb_token_access = result["wb_token_access"]
        return WbUserAuthData(
            wb_user_id=wb_user_id,
            wb_supplier_id=wb_supplier_id,
            wb_token_access=wb_token_access,
        )
