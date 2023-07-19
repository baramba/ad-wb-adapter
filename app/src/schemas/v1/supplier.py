import uuid
from typing import TypeVar

from pydantic import Field

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


class Balance(BaseOrjsonModel):
    # Счёт, рублей
    account: int = Field(description="Счёт, рублей")
    # Баланс, рублей
    balance: int = Field(description="Баланс, рублей")
    # Бонусы, рублей
    bonus: int | None = Field(description="Бонусы, рублей")


class BalanceResponse(BaseResponseSuccess):
    payload: Balance
