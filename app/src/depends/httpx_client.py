import httpx


from core.settings import settings

proxies: dict[str, str] | None = None

if settings.PROXY_URL:
    proxies = {
        "http://": settings.PROXY_URL,
        "https://": settings.PROXY_URL,
    }

client = httpx.AsyncClient(proxies=proxies)  # type: ignore [arg-type]


async def get_http_client() -> httpx.AsyncClient:
    return client
