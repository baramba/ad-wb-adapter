from schemas.common import BaseOrjsonModel


class WbUserAuthDataDTO(BaseOrjsonModel):
    wb_user_id: int
    wb_supplier_id: str
    wb_token_access: str | None = None
    wb_token_standart: str | None = None
    wb_token_stat: str | None = None
    wb_token_ad: str
