import contextlib
import json
import random
from urllib.parse import unquote

import httpx

from core.settings import logger
from dto.token import WbUserAuthDataDTO


class BaseWBAdapter:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.http_client.event_hooks = {
            "request": [self._log_request],
            "response": [self._log_response],
        }
        self._auth_data: WbUserAuthDataDTO | None = None

    @property
    def auth_data(self) -> WbUserAuthDataDTO | None:
        return self._auth_data

    @auth_data.setter
    def auth_data(self, auth_data: WbUserAuthDataDTO) -> None:
        self._auth_data = auth_data

    @staticmethod
    def random_device() -> str:
        devices = (
            "Chrome 113.0",
            "Chrome 97.0",
            "Mozilla 2.2",
            "Mozilla 1.9",
            "Safari 15.0",
            "Safari 6.0",
            "Opera 80.0",
            "Edge 93.0",
        )
        return f"Unknown, {random.choice(devices)}"

    def _cut_string(self, string: str, length: int) -> str:
        string = string.replace("\n", "")
        return "{0} {1}".format(string[:length], "..." * (len(string) > length))

    async def _log_request(self, request: httpx.Request) -> None:
        content: str = request.content.decode("utf-8")

        with contextlib.suppress(ValueError):
            content = json.loads(content)

        logger.debug(
            "{0}: {1}, data: {2}".format(
                request.method,
                unquote(str(request.url)),
                str(content),
            )
        )

    async def _log_response(self, response: httpx.Response) -> None:
        request = response.request
        content: str = (await response.aread()).decode("utf-8")
        logger.debug(
            "{0}: {1}, {2}, data: {3}".format(
                request.method,
                unquote(str(request.url)),
                response.status_code,
                content,
            )
        )

    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = {} or headers
        cookies = {} or cookies
        body = {} or body
        response: httpx.Response = await self.http_client.post(
            url=url,
            headers=headers,
            cookies=cookies,
            json=body,
        )
        return response

    async def _put(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = {} or headers
        cookies = {} or cookies
        body = {} or body
        response: httpx.Response = await self.http_client.put(
            url=url,
            headers=headers,
            cookies=cookies,
            json=body,
        )
        return response

    async def _get(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        headers = {} or headers
        cookies = {} or cookies
        params = {} or params
        response: httpx.Response = await self.http_client.get(
            url=url,
            headers=headers,
            cookies=cookies,
            params=params,
        )
        return response

    # def __getattribute__(self, name: str) -> Any | None:
    #     #  Проверяем, что _auth_data is not None.
    #     attr = super().__getattribute__(name)
    #     if callable(attr) and super().__getattribute__("auth_data") is None:
    #         raise ValueError(
    #             "Значние атрибута CampaignAdapter.auth_data = None. Для корректной работы адаптера установите \
    #             авторизационные данные."
    #         )
    #     return super().__getattribute__(name)
