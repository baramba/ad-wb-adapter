import uuid
from typing import TypeVar

from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponseSuccess

T = TypeVar("T")


class WBTokenRequest(BaseOrjsonModel):
    wb_token_refresh: str
    wb_user_id: int
    wb_supplier_id: uuid.UUID


class WBToken(BaseOrjsonModel):
    wb_token_access: str


class WBTokenResponse(BaseResponseSuccess):
    payload: WBToken
