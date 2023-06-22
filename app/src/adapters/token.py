import uuid

from httpx import ConnectError
from pydantic import ValidationError

from adapters.gen.token.token.client import Client
from adapters.gen.token.token.client.api.auth_data import (
    get_auth_data_v1_auth_data_get,
    update_wb_token_v1_auth_data_update_get,
)
from adapters.gen.token.token.client.models import AuthDataGetResponse
from adapters.gen.token.token.client.models.http_validation_error import HTTPValidationError
from core.settings import logger, settings
from dto.token import OfficialUserAuthDataDTO, UnofficialUserAuthDataDTO, UserAuthDataDTO
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

    async def auth_data_by_user_id(self, user_id: uuid.UUID) -> UserAuthDataDTO:
        auth_data: AuthDataGetResponse | HTTPValidationError | None = None
        try:
            auth_data = await get_auth_data_v1_auth_data_get.asyncio(
                client=self.client,
                user_id=str(user_id),
            )
        except ConnectError as e:
            logger.error(f"Не удалось подключиться к token manager ({self.url}). error: {e}")

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
        return UserAuthDataDTO(
            wb_supplier_id=auth_data.wb_supplier_id,
            wb_token_access=auth_data.wb_token_access,
            wb_user_id=auth_data.wb_user_id,
            wb_token_ad=auth_data.wb_token_ad,
            # wb_token_standart=str(auth_data.wb_token_standart),
            # wb_token_stat=str(auth_data.wb_token_stat),
        )

    async def auth_data_by_user_id_official(self, user_id: uuid.UUID) -> OfficialUserAuthDataDTO:
        auth_data: UserAuthDataDTO = await self.auth_data_by_user_id(user_id)
        try:
            return OfficialUserAuthDataDTO.parse_obj(auth_data.dict())
        except ValidationError as e:
            logger.error(e.errors())
            raise WBAError(
                description=f"Не найден wb_token_ad для пользователя user_id={user_id}.",
            ) from e

    async def auth_data_by_user_id_unofficial(self, user_id: uuid.UUID) -> UnofficialUserAuthDataDTO:
        auth_data: UserAuthDataDTO = await self.auth_data_by_user_id(user_id)
        try:
            return UnofficialUserAuthDataDTO.parse_obj(auth_data.dict())
        except ValidationError as e:
            logger.error(e.errors())
            raise WBAError(
                description=f"Не найдены авторизационные данные для пользователя user_id={user_id}.",
            ) from e

    async def request_update_user_access_token(self, user_id: uuid.UUID, wb_token_access: str) -> None:
        await update_wb_token_v1_auth_data_update_get.asyncio(
            client=self.client,
            user_id=str(user_id),
            wb_token_access=wb_token_access,
        )
        logger.debug(f"Отправлен запрос на обновление wb_token_access для user_id:{user_id}.")
