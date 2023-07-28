from schemas.common import BaseOrjsonModel


class UserAuthDataBase(BaseOrjsonModel):
    wb_user_id: int | None = None
    wb_supplier_id: str | None = None
    wb_token_access: str | None = None
    wb_token_standart: str | None = None
    wb_token_stat: str | None = None
    wb_token_ad: str | None = None


class OfficialUserAuthDataDTO(UserAuthDataBase):
    wb_token_ad: str


class UnofficialUserAuthDataDTO(UserAuthDataBase):
    wb_user_id: int
    wb_supplier_id: str
    wb_token_access: str
    wb_token_standart: str | None = None
    wb_token_stat: str | None = None
    wb_token_ad: str
