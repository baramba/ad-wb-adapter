import contextlib
import json
import random
from http import HTTPStatus
from urllib.parse import unquote

import backoff
import httpx

from core.settings import logger, settings
from dto.token import WbUserAuthDataDTO


def retry_then_5xx(e: Exception) -> bool:
    status = e.response.status_code  # type: ignore[attr-defined]
    return not (status == HTTPStatus.TOO_MANY_REQUESTS or (500 <= status < 600))


class BaseWBAdapter:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.http_client.event_hooks = {
            "request": [self._log_request],
            "response": [self._log_response],
        }
        self._auth_data: WbUserAuthDataDTO | None = None
        self.max_tries: int = 5

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
            "{0}: {1}, status: {2}, data: {3}".format(
                request.method,
                unquote(str(request.url)),
                response.status_code,
                content,
            )
        )

    @backoff.on_exception(
        backoff.fibo,
        exception=httpx.HTTPStatusError,
        max_time=settings.WBADAPTER.MAX_RETRY_TIME,
        giveup=retry_then_5xx,
        jitter=None,
    )
    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = headers or {}
        cookies = cookies or {}
        body = body or {}
        response: httpx.Response = await self.http_client.post(
            url=url,
            headers=headers,
            cookies=cookies,
            json=body,
        )
        response.raise_for_status()
        return response

    @backoff.on_exception(
        backoff.fibo,
        exception=httpx.HTTPStatusError,
        max_time=settings.WBADAPTER.MAX_RETRY_TIME,
        giveup=retry_then_5xx,
        jitter=None,
    )
    async def _put(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = headers or {}
        cookies = cookies or {}
        body = body or {}
        response: httpx.Response = await self.http_client.put(
            url=url,
            headers=headers,
            cookies=cookies,
            json=body,
        )
        response.raise_for_status()
        return response

    @backoff.on_exception(
        backoff.fibo,
        exception=httpx.HTTPStatusError,
        max_time=settings.WBADAPTER.MAX_RETRY_TIME,
        giveup=retry_then_5xx,
        jitter=None,
    )
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
        response: httpx.Response = await self.http_client.get(
            url=url,
            headers=headers,
            cookies=cookies,
            params=params,
        )
        response.raise_for_status()
        return response
