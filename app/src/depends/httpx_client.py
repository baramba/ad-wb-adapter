import httpx

client = httpx.AsyncClient()


async def get_client() -> httpx.AsyncClient:
    return client
