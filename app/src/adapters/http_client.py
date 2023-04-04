import asyncio
from functools import wraps
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

    async def _post(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
        method: str = __name__,
    ) -> httpx.Response:
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        body = dict() if body is None else body

        logger.info("{0}:{1}".format(__name__, url))

        response: httpx.Response = await self.client.post(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
            json=body,
        )
        logger.info("{0}, {1}, {2}".format(method, url, response))
        return response

    async def _put(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        body: dict | None = None,
        method: str = __name__,
    ) -> httpx.Response:
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        body = dict() if body is None else body

        logger.info("{0}, {1}, {2}".format(method, url, body))
        response: httpx.Response = await self.client.put(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
            json=body,
        )
        logger.info("{0}, {1}, {2}".format(method, url, response))
        return response

    async def _get(
        self,
        url: str,
        headers: dict | None = None,
        cookies: dict | None = None,
        query: dict | None = None,
        method: str = __name__,
    ) -> httpx.Response:
        headers = dict() if headers is None else headers
        cookies = dict() if cookies is None else cookies
        query = dict() if query is None else query

        logger.info("{0}, {1}, {2}".format(method, url, query))
        response: httpx.Response = await self.client.get(
            url=url,
            headers=self.headers | headers,
            cookies=self.cookies | cookies,
            params=query,
        )
        logger.info("{0}, {1}, {2}".format(method, url, response))

        return response


def retry_ahttpx(codes: tuple[str, ...], retries: int = 5):
    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            for _ in range(retries):
                result: httpx.Response = await func(*args, **kwargs)
                if any([code in str(result.status_code) for code in codes]):
                    await asyncio.sleep(2)
                    continue
                return result
            result.raise_for_status()

        return inner

    return func_wrapper
