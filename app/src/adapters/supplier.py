import uuid

from httpx import HTTPStatusError, Response
from adapters.wb_http_adapter import HTTPAdapter
from exceptions.supplier import SupplierWBTokenError
from schemas.v1.base import ResponseStatus


class SupplierAdapter(HTTPAdapter):
    async def wb_user_auth(
        self, wb_token_refresh: str, wb_x_supplier_id_external: uuid.UUID
    ) -> str:
        """Авторизует пользователя wildberries и возвращает WBToken (cmp.wildberries.ru).

        Returns:
            wb_token_access: str
        """
        self.wb_token_refresh = wb_token_refresh
        self.wb_x_supplier_id_external: str = str(wb_x_supplier_id_external)
        token = await self._wb_grant()
        wb_token_access = await self._wb_login(token)
        await self._wb_introspect(wb_token_access=wb_token_access)
        return wb_token_access

    async def _wb_grant(self) -> str:
        url: str = "https://passport.wildberries.ru/api/v2/auth/grant"
        referer: str = "https://cmp.wildberries.ru/"
        try:
            headers = {"Referer": referer}
            cookies: dict = {
                "WBToken": self.wb_token_refresh,
                "x-supplier-id-external": self.wb_x_supplier_id_external,
            }
            result: Response = await self._post(
                url=url, cookies=cookies, headers=headers
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise SupplierWBTokenError(
                status=ResponseStatus.ERROR,
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_grant) WBToken.",
            )
        token: str = result.json()["token"]
        return token

    async def _wb_login(self, token: str) -> str:
        url: str = "https://cmp.wildberries.ru/passport/api/v2/auth/login"
        referer: str = "https://cmp.wildberries.ru/campaigns/list/all?type=auction"
        try:
            headers = {"Referer": referer}
            cookies: dict = {
                "x-supplier-id-external": self.wb_x_supplier_id_external,
            }
            body = {
                "token": token,
                "device": self.ua.random,
            }
            result: Response = await self._post(
                url=url, cookies=cookies, body=body, headers=headers
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise SupplierWBTokenError(
                status=ResponseStatus.ERROR,
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_login) WBToken.",
            )
        wb_token_access = str(result.cookies["WBToken"])
        return wb_token_access

    async def _wb_introspect(self, wb_token_access: str) -> None:
        url: str = "https://cmp.wildberries.ru/passport/api/v2/auth/introspect"
        referer: str = "https://cmp.wildberries.ru/campaigns/list/all?type=auction"

        try:
            headers = {"Referer": referer}
            cookies: dict = {
                "x-supplier-id-external": self.wb_x_supplier_id_external,
                "WBToken": wb_token_access,
            }
            result: Response = await self._get(
                url=url, cookies=cookies, headers=headers
            )
            result.raise_for_status()
        except HTTPStatusError as e:
            raise SupplierWBTokenError(
                status=ResponseStatus.ERROR,
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_login) WBToken.",
            )
