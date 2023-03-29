import uuid

from pydantic import BaseModel


class RabbitJobResult(BaseModel):
    job_id: uuid.UUID
