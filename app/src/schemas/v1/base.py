import uuid

from pydantic import BaseModel


class RequestQueuedResponse(BaseModel):
    job_id: uuid.UUID


class JobResult(BaseModel):
    """Check requested route to get job result response schema"""

    class Config:
        extra = 'allow'
