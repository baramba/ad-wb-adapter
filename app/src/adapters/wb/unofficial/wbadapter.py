import fake_useragent as fk_ua
import httpx

from adapters.wb.wbadapter import BaseWBAdapter
from dto.token import WbUserAuthDataDTO

browsers = ["chrome", "opera", "firefox", "edge"]


class WBAdapterUnofficial(BaseWBAdapter):
    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client=http_client)
        self.ua: fk_ua.FakeUserAgent = fk_ua.UserAgent(browsers=browsers)
        self.headers: dict[str, str] = {
            "User-Agent": self.ua.random,
        }
        self.cookies: dict = {}

    @property
    def auth_data(self) -> WbUserAuthDataDTO | None:
        return super().auth_data

    @auth_data.setter
    def auth_data(self, auth_data: WbUserAuthDataDTO) -> None:
        self._auth_data = auth_data
        self.headers["X-User-Id"] = str(auth_data.wb_user_id)
        self.cookies["x-supplier-id-external"] = auth_data.wb_supplier_id
        self.cookies["WBToken"] = auth_data.wb_token_access

    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = headers or {}
        cookies = cookies or {}
        headers |= self.headers
        cookies |= self.cookies

        body = body or {}
        response: httpx.Response = await super()._post(url, headers, cookies, body)
        return response

    async def _put(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = headers or {}
        cookies = cookies or {}
        headers |= self.headers
        cookies |= self.cookies
        body = body or {}
        response: httpx.Response = await super()._put(url, headers, cookies, body)
        return response

    async def _get(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = headers or {}
        cookies = cookies or {}
        params = params or {}
        headers |= self.headers
        cookies |= self.cookies

        response: httpx.Response = await super()._get(url, headers, cookies, params)
        return response
