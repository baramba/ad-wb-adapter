from adapters.token import TokenManager


async def get_token_manager() -> TokenManager:
    return TokenManager()
