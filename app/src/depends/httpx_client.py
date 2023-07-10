import httpx

from core.settings import settings


async def get_http_client() -> httpx.AsyncClient:
    proxies: dict[str, str] | None = None

    if settings.WBADAPTER.PROXY_URL:
        proxies = {
            "http://": settings.WBADAPTER.PROXY_URL,
            "https://": settings.WBADAPTER.PROXY_URL,
        }
    transport = httpx.AsyncHTTPTransport(retries=3)
    return httpx.AsyncClient(proxies=proxies, transport=transport)  # type: ignore [arg-type]
