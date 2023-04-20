import httpx

client = httpx.AsyncClient()


async def get_http_client() -> httpx.AsyncClient:
    return client
