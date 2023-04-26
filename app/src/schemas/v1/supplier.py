from typing import Generic, TypeVar
import uuid

from pydantic import UUID4

from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponse, ResponseCode, ResponseStatus

T = TypeVar("T")


class WBTokenRequest(BaseOrjsonModel):
    wb_token_refresh: str
    wb_user_id: int
    wb_supplier_id: uuid.UUID


class WBToken(BaseOrjsonModel):
    wb_token: str


class WBTokenResponse(BaseResponse, Generic[T]):
    body: T | None = None
    status: ResponseStatus
    status_code: int


class WBTokenSuccessResponse(WBTokenResponse):
    status: ResponseStatus = ResponseStatus.OK
    status_code: ResponseCode = ResponseCode.OK
    body: WBToken


class WBTokenErrorResponse(WBTokenResponse):
    status: ResponseStatus = ResponseStatus.ERROR
    status_code: int = ResponseCode.OK


class WbUserAuthData(BaseOrjsonModel):
    wb_user_id: int
    wb_supplier_id: UUID4
    wb_token_access: str
