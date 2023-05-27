import uuid

from adapters.gen.token.token.client.models.http_validation_error import (
    HTTPValidationError,
)
from adapters.http_adapter import HTTPAdapter
from core.settings import settings
from dto.supplier import WbUserAuthDataDTO

from adapters.gen.token.token.client import Client
from adapters.gen.token.token.client.models import AuthDataGetResponse
from adapters.gen.token.token.client.api.auth_data import (
    get_auth_data_api_v1_auth_data_get,
)
from exceptions.base import WBAError
from core.settings import logger


class TokenManager:
    def __init__(self, client: HTTPAdapter) -> None:
        self.url = settings.TOKEN_MANAGER_URL
        self.client = client

    # async def auth_data_by_user_id_old(self, user_id: uuid.UUID) -> WbUserAuthDataDTO:
    #     url = f"{self.url}/auth_data"
    #     params = {"user_id": user_id}

    #     try:
    #         response = await self.client._get(url=url, params=params)
    #         response.raise_for_status()
    #     except HTTPStatusError as e:
    #         raise WBAError(
    #             status_code=e.response.status_code,
    #             description=f"Ошибка при получении авторизационных данных пользователя user_id={user_id}",
    #         )
    #     return WbUserAuthDataDTO.parse_obj(response.json())

    async def auth_data_by_user_id(self, user_id: uuid.UUID) -> WbUserAuthDataDTO:
        client = Client(
            base_url=settings.TOKEN_MANAGER_URL,
            timeout=5,
            verify_ssl=True,
            follow_redirects=True,
            raise_on_unexpected_status=True,
        )

        auth_data: AuthDataGetResponse | HTTPValidationError | None = (
            await get_auth_data_api_v1_auth_data_get.asyncio(
                client=client,
                user_id=str(user_id),
            )
        )
        if not auth_data or isinstance(auth_data, HTTPValidationError):
            logger.error(
                "Ошибка при получении авторизационных данных. auth_data={auth_data}"
            )
            raise WBAError(
                description=f"Ошибка при получении авторизационных данных пользователя user_id={user_id}",
            )
        logger.debug(f"user_id:{user_id}, auth_data: {auth_data}")
        return WbUserAuthDataDTO(
            wb_supplier_id=auth_data.wb_supplier_id,
            wb_token_access=auth_data.wb_token_access,
            wb_user_id=auth_data.wb_user_id,
        )
