from fastapi import FastAPI

from core.settings import settings
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
    servers=[{"url": settings.CONTEXT}],
)


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
            "Path": settings.BASE_DIR,
        },
    }


app.include_router(v1.router)
