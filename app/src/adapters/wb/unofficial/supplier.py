import uuid

from httpx import HTTPStatusError, Response

from adapters.wb.unofficial.wbadapter import WBAdapterUnofficial
from exceptions.base import WBAError
from schemas.v1.base import ResponseCode


class SupplierAdapter(WBAdapterUnofficial):
    async def wb_user_auth(self, wb_token_refresh: str, wb_x_supplier_id_external: uuid.UUID) -> str:
        """Авторизует пользователя wildberries и возвращает WBToken (cmp.wildberries.ru).

        Returns:
            wb_token_access: str
        """
        self.wb_token_refresh = wb_token_refresh
        self.wb_x_supplier_id_external: str = str(wb_x_supplier_id_external)
        token = await self._wb_grant()
        wb_token_access: str = await self._wb_login(token)
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
            result: Response = await self._post(url=url, cookies=cookies, headers=headers)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_grant) WBToken.",
            ) from e
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
                "device": self.random_device(),
            }
            result: Response = await self._post(url=url, cookies=cookies, body=body, headers=headers)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_login) WBToken.",
            ) from e
        try:
            wb_token_access: str = str(result.cookies["WBToken"])
        except KeyError as exc:
            raise WBAError(
                status_code=ResponseCode.ERROR,
                description="Ошибка при получении(wb_login) WBToken. Не удалось прочитать cookies=WBToken.",
            ) from exc
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
            await self._get(url=url, cookies=cookies, headers=headers)
        except HTTPStatusError as e:
            raise WBAError(
                status_code=e.response.status_code,
                description="Ошибка при получении(wb_login) WBToken.",
            ) from e
