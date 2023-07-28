import uuid

from adapters.gen.token.token.client import Client
from adapters.gen.token.token.client.api.auth_data import (
    get_auth_data_v1_auth_data_get,
    update_wb_token_v1_auth_data_update_get,
)
from adapters.gen.token.token.client.models import AuthDataGetResponse
from adapters.gen.token.token.client.models.http_validation_error import HTTPValidationError
from core.settings import logger, settings
from dto.token import OfficialUserAuthDataDTO, UnofficialUserAuthDataDTO, UserAuthDataBase
from exceptions.base import WBAError
from httpx import ConnectError
from pydantic import ValidationError


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

    async def auth_data_by_user_id(self, user_id: uuid.UUID) -> UserAuthDataBase:
        auth_data: AuthDataGetResponse | HTTPValidationError | None = None
        try:
            auth_data = await get_auth_data_v1_auth_data_get.asyncio(
                client=self.client,
                x_user_id=str(user_id),
            )

        except ConnectError as e:
            logger.error(f"Could not connect to token manager ({self.url}). error: {e}")

        if isinstance(auth_data, HTTPValidationError):
            logger.error(
                f"An error occurred while obtaining authorization data. user_id={user_id}, error={auth_data.detail}"
            )
            raise WBAError(
                description=f"An error occurred while obtaining authorization data. user_id={user_id}",
            )

        if not auth_data:
            logger.error(f"User's authorization data not found. user_id={user_id}")
            raise WBAError(
                description=f"User's authorization data not found. user_id={user_id}",
            )

        logger.debug(
            "Authorization data received - user_id:{0}, wb_supplier_id: {1}, wb_user_id:{2}".format(
                user_id,
                auth_data.wb_supplier_id,
                auth_data.wb_user_id,
            )
        )
        auth_data_dict = auth_data.to_dict()
        return UserAuthDataBase(
            wb_supplier_id=auth_data_dict.get("wb_supplier_id"),
            wb_token_access=auth_data_dict.get("wb_token_access"),
            wb_user_id=auth_data_dict.get("wb_user_id"),
            wb_token_ad=auth_data_dict.get("wb_token_ad"),
        )

    async def auth_data_by_user_id_official(self, user_id: uuid.UUID) -> OfficialUserAuthDataDTO:
        auth_data: UserAuthDataBase = await self.auth_data_by_user_id(user_id)
        try:
            return OfficialUserAuthDataDTO.parse_obj(auth_data.dict())
        except ValidationError as e:
            logger.error(e.errors())
            raise WBAError(
                description=f"Can't find wb_token_ad for user_id={user_id}.",
            ) from e

    async def auth_data_by_user_id_unofficial(self, user_id: uuid.UUID) -> UnofficialUserAuthDataDTO:
        auth_data: UserAuthDataBase = await self.auth_data_by_user_id(user_id)
        try:
            return UnofficialUserAuthDataDTO.parse_obj(auth_data.dict())
        except ValidationError as e:
            logger.error(e.errors())
            raise WBAError(
                description=f"Can't find authorization data for user_id={user_id}.",
            ) from e

    async def request_update_user_access_token(self, user_id: uuid.UUID, wb_token_access: str) -> None:
        await update_wb_token_v1_auth_data_update_get.asyncio(
            client=self.client,
            x_user_id=str(user_id),
            wb_token_access=wb_token_access,
        )
        logger.debug(f"Send request to update wb_token_access for user_id:{user_id}.")
