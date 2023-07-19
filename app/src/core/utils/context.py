import uuid
from contextvars import ContextVar

# extra_log_params_middleware
campaign_id: ContextVar[str | None] = ContextVar("campaign_id", default="")
wb_campaign_id: ContextVar[str | None] = ContextVar("wb_campaign_id", default="")
subject_id: ContextVar[str | None] = ContextVar("subject_id", default="")
user_id: ContextVar[str | None] = ContextVar("user_id", default="")


class AppContext:
    @staticmethod
    def user_id() -> uuid.UUID:
        if user_id_ := user_id.get():
            return uuid.UUID(user_id_)
        raise TypeError("user_id is not define.")
