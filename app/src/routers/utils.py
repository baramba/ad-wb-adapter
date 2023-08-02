import uuid
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer()


def x_user_id(x_user_id: Annotated[uuid.UUID, Header()], token: Annotated[str, Depends(http_bearer)]) -> uuid.UUID:
    return x_user_id
