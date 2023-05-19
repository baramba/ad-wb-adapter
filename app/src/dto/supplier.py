from pydantic import UUID4
from schemas.common import BaseOrjsonModel


class WbUserAuthDataDTO(BaseOrjsonModel):
    wb_user_id: int
    wb_supplier_id: UUID4
    wb_token_access: str
