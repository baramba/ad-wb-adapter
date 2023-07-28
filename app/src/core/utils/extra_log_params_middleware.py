from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from core.utils.context import campaign_id, subject_id, user_id, wb_campaign_id


class LogExtraParamsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope)
            campaign_id.set(request.query_params.get("campaign_id"))
            subject_id.set(request.query_params.get("subject_id"))
            user_id.set(request.headers.get("x-user-id"))
            wb_campaign_id.set(request.query_params.get("wb_campaign_id"))

        await self.app(scope, receive, send)
