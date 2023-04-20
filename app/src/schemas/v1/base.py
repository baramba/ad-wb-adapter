from enum import Enum, IntEnum
import uuid
from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel
from schemas.common import BaseOrjsonModel

T = TypeVar("T")


class RequestQueuedResponse(BaseOrjsonModel):
    job_id: uuid.UUID


class JobResult(GenericModel, Generic[T]):
    code: str
    status_code: int = 200
    text: Optional[str] = None
    response: T

    class Config:
        extra = "allow"


class ResponseStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


class ResponseCode(IntEnum):
    OK = 200
    ERROR = 999


class BaseResponse(BaseOrjsonModel):
    status: ResponseStatus
    status_code: int
    description: str | None = None
