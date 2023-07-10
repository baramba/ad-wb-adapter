from logging import Filter, LogRecord

from asgi_correlation_id.context import correlation_id

from core.utils.context import campaign_id, subject_id, user_id, wb_campaign_id


class ExtraParamsFilter(Filter):
    """Logging filter to attached extra log params"""

    def __init__(self, name: str = ""):
        super().__init__(name=name)

    def filter(self, record: LogRecord) -> bool:
        setattr(record, "adpine.wb_campaign_id", wb_campaign_id.get())
        setattr(record, "adpine.campaign_id", campaign_id.get())
        setattr(record, "adpine.subject_id", subject_id.get())
        setattr(record, "adpine.user_id", user_id.get())
        setattr(record, "adpine.request_id", correlation_id.get())
        return True
