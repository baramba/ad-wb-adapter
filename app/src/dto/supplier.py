from schemas.common import BaseOrjsonModel


class WbUserAuthDataDTO(BaseOrjsonModel):
    wb_user_id: int
    wb_supplier_id: str
    wb_token_access: str
