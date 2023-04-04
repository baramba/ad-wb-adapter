from routers import v1
from routers import metadata
from fastapi import FastAPI

from core.settings import settings
from depends import shutdown as sd, startup as su
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    openapi_tags=metadata.tags,
    description=metadata.description,
)


@app.on_event("startup")
async def startup():
    await su.startup()


@app.on_event("shutdown")
async def shutdown():
    await sd.shutdown()


@app.get("/", tags=["about"])
async def root():
    return {
        "message": {
            "Project": settings.PROJECT_NAME,
            "Path": settings.BASE_DIR,
        },
    }


app.include_router(v1.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
