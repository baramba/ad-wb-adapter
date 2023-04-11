import uuid
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class RequestQueuedResponse(BaseModel):
    job_id: uuid.UUID


class JobResult(GenericModel, Generic[T]):
    """Check requested route to get job result response schema"""

    code: str
    status_code: int = 200
    text: Optional[str] = None
    response: T

    class Config:
        extra = "allow"
