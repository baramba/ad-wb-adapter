from contextvars import ContextVar

# extra_log_params_middleware
campaign_id: ContextVar[str | None] = ContextVar("campaign_id", default="")
wb_campaign_id: ContextVar[str | None] = ContextVar("wb_campaign_id", default="")
subject_id: ContextVar[str | None] = ContextVar("subject_id", default="")
user_id: ContextVar[str | None] = ContextVar("user_id", default="")
