import httpx

from adapters.wb.wbadapter import BaseWBAdapter
from dto.token import OfficialUserAuthDataDTO, UserAuthDataBase


class WBAdapter(BaseWBAdapter):
    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client=http_client)
        self.headers: dict = {}
        self.cookies: dict = {}
        self._auth_data: OfficialUserAuthDataDTO | None = None

    @property
    def auth_data(self) -> UserAuthDataBase | None:
        return self._auth_data

    @auth_data.setter
    def auth_data(self, auth_data: OfficialUserAuthDataDTO) -> None:
        self._auth_data = auth_data
        self.headers["Authorization"] = auth_data.wb_token_ad

    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        if headers is None:
            headers = dict(self.headers)
        if cookies is None:
            cookies = dict(self.cookies)

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
        if headers is None:
            headers = dict(self.headers)
        if cookies is None:
            cookies = dict(self.cookies)
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
        if headers is None:
            headers = dict(self.headers)
        if cookies is None:
            cookies = dict(self.cookies)
        response: httpx.Response = await super()._get(url, headers, cookies, params)
        return response
