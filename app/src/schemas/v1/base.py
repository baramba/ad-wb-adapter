from enum import Enum, IntEnum
import uuid
from typing import Generic, Optional, TypeVar
from fastapi import Response
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
    NO_CONTENT = "no_content"


class ResponseCode(IntEnum):
    OK = 200
    NO_CONTENT = 204
    ERROR = 999


class BaseResponse(BaseOrjsonModel, Response, Generic[T]):
    status: ResponseStatus
    status_code: int
    description: str | None = None
    payload: T | None = None


class BaseResponseEmpty(BaseResponse):
    status: ResponseStatus = ResponseStatus.NO_CONTENT
    status_code: int = ResponseCode.NO_CONTENT
    description: str | None = "В ответ на запрос получен пустой ответ."


class BaseResponseError(BaseResponse):
    status: ResponseStatus = ResponseStatus.ERROR
    status_code: int = ResponseCode.ERROR
    description = "Произошла непредвиденная ошибка. Обратитесь к администратору."


class BaseResponseSuccess(BaseResponse):
    status: ResponseStatus = ResponseStatus.OK
    status_code: int = ResponseCode.OK
