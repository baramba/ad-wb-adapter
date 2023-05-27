from typing import AsyncGenerator
import httpx

client = httpx.AsyncClient()


async def get_http_client_XX() -> AsyncGenerator[httpx.AsyncClient, None]:
    try:
        yield client
    finally:
        await client.aclose()
