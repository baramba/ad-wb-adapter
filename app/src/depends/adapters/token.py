from adapters.http_adapter import HTTPAdapter

from adapters.token_manager import TokenManager
from depends.adapters.http_adapter import get_http_adapter


async def get_token_manager_adapter() -> TokenManager:
    client: HTTPAdapter = await get_http_adapter()
    return TokenManager(client=client)
