import contextlib
import json

import fake_useragent as fk_ua
import httpx
from core.settings import logger


class HTTPAdapter:
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.ua: fk_ua.FakeUserAgent = fk_ua.UserAgent()
        self.client = client
        self.headers = {
            "User-Agent": self.ua.random,
        }
        self.client.event_hooks = {
            "request": [self.log_request],
            "response": [self.log_response],
        }

    def cut_string(self, string: str, length: int) -> str:
        string = string.replace("\n", "")
        return "{0} {1}".format(string[:length], "..." * (len(string) > length))

    async def log_request(self, request: httpx.Request) -> None:
        content: str = request.content.decode("utf-8")

        with contextlib.suppress(ValueError):
            content = json.loads(content)

        logger.info(
            "{0}: {1}, data: {2}".format(
                request.method,
                request.url,
                self.cut_string(str(content), 75),
            )
        )

    async def log_response(self, response: httpx.Response) -> None:
        request = response.request
        content: str = (await response.aread()).decode("utf-8")
        logger.info(
            "{0}: {1}, {2}, data: {3}".format(
                request.method,
                request.url,
                response.status_code,
                self.cut_string(str(content), 75),
            )
        )

    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response:
        headers = headers or self.headers
        cookies = cookies or self.headers
        response: httpx.Response = await self.client.post(
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
        headers = headers or self.headers
        cookies = cookies or self.headers

        response: httpx.Response = await self.client.put(
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
        query: dict | None = None,
    ) -> httpx.Response:
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        query = dict() if query is None else query
        headers = headers or self.headers
        cookies = cookies or self.headers
        response: httpx.Response = await self.client.get(
            url=url,
            headers=headers,
            cookies=cookies,
            params=query,
        )
        return response
