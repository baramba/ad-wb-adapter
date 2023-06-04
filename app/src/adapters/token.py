import uuid

from httpx import ConnectError

from adapters.gen.token.token.client import Client
from adapters.gen.token.token.client.api.auth_data import (
    get_auth_data_api_v1_auth_data_get,
    update_wb_token_api_v1_auth_data_update_get,
)
from adapters.gen.token.token.client.models import AuthDataGetResponse
from adapters.gen.token.token.client.models.http_validation_error import HTTPValidationError
from core.settings import logger, settings
from dto.token import WbUserAuthDataDTO
from exceptions.base import WBAError


class TokenManager:
    def __init__(self) -> None:
        self.url = settings.TOKEN_MANAGER_URL
        self.client = Client(
            base_url=settings.TOKEN_MANAGER_URL,
            timeout=5,
            verify_ssl=True,
            follow_redirects=True,
            raise_on_unexpected_status=True,
        )

    async def auth_data_by_user_id(self, user_id: uuid.UUID) -> WbUserAuthDataDTO:
        try:
            auth_data: AuthDataGetResponse | HTTPValidationError | None = (
                await get_auth_data_api_v1_auth_data_get.asyncio(
                    client=self.client,
                    user_id=str(user_id),
                )
            )
        except ConnectError:
            logger.error(f"Не удалось подключиться к token manager ({self.url}).")
            raise

        if not auth_data or isinstance(auth_data, HTTPValidationError):
            logger.error(f"Ошибка при получении авторизационных данных. user_id={user_id}")
            raise WBAError(
                description=f"Ошибка при получении авторизационных данных пользователя user_id={user_id}",
            )
        logger.debug(
            "Получены авторизационные данные - user_id:{0}, wb_supplier_id: {1}, wb_user_id:{2}".format(
                user_id,
                auth_data.wb_supplier_id,
                auth_data.wb_user_id,
            )
        )
        return WbUserAuthDataDTO(
            wb_supplier_id=auth_data.wb_supplier_id,
            wb_token_access=auth_data.wb_token_access,
            wb_user_id=auth_data.wb_user_id,
            wb_token_ad=auth_data.wb_token_ad,
        )

    async def request_update_user_access_token(self, user_id: uuid.UUID, wb_token_access: str) -> None:
        await update_wb_token_api_v1_auth_data_update_get.asyncio(
            client=self.client,
            user_id=str(user_id),
            wb_token_access=wb_token_access,
        )
        logger.debug(f"Отправлен запрос на обновление wb_token_access для user_id:{user_id}.")
