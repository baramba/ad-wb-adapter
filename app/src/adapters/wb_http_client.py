import asyncio
import contextlib
from functools import wraps
import json
import httpx
import fake_useragent as fk_ua
from core.settings import logger


class BaseAdapter:
    headers: dict
    cookies: dict

    def __init__(
        self,
        client: httpx.AsyncClient,
        user_id: str,
        supplier_id: str,
        supplier_id_external: str,
        wb_token: str,
        referer: str = "https://cmp.wildberries.ru",
    ):
        self.client = client
        self.headers = {
            "User-Agent": fk_ua.UserAgent()["google_chrome"],
            "X-User-Id": user_id,
            "Referer": referer,
        }
        self.cookies = {
            "x-supplier-id": supplier_id,
            "x-supplier-id-external": supplier_id_external,
            "WBToken": wb_token,
        }
        self.client.event_hooks = {
            "request": [self.log_request],
            "response": [self.log_response],
        }

    def cut_string(self, string: str, length: int) -> str:
        string = string.replace("\n", "")
        return "{0} {1}".format(string[:length], "..." * (len(string) > length))

    async def log_request(self, request: httpx.Request):
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

    async def log_response(self, response: httpx.Response):
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
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        body = dict() if body is None else body

        response: httpx.Response = await self.client.post(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
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
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        body = dict() if body is None else body

        response: httpx.Response = await self.client.put(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
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

        response: httpx.Response = await self.client.get(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
            params=query,
        )
        return response
