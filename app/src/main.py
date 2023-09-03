from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI

from core.settings import settings
from core.utils.extra_log_params_middleware import LogExtraParamsMiddleware
from depends import shutdown as sd
from depends import startup as su
from routers import metadata, v1

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs/swagger",
    openapi_url="/docs/openapi",
    openapi_tags=metadata.tags,
    description=metadata.description,
    root_path=settings.CONTEXT,
)
app.openapi_version = "3.0.0"
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-Id",
    update_request_header=True,
    generator=lambda: uuid4().hex,
    validator=is_valid_uuid4,
)
app.add_middleware(LogExtraParamsMiddleware)


@app.on_event("startup")
async def startup() -> None:
    await su.startup()


@app.on_event("shutdown")
async def shutdown() -> None:
    await sd.shutdown()


@app.get("/about", tags=["about"])
async def root() -> dict[str, dict]:
    return {
        "message": {
            "Project": settings.PROJECT_NAME,
            "Path": settings.WBADAPTER.BASE_DIR,
        },
    }


app.include_router(v1.router)
