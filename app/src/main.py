import endpoints

from fastapi import FastAPI

from core.settings import settings
from depends import shutdown as sd, startup as su
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME,
              docs_url='/api/docs',
              openapi_url='/api/openapi.json', )
origins = ['*']


@app.on_event('startup')
async def startup():
    await su.startup()


@app.on_event('shutdown')
async def shutdown():
    await sd.shutdown()


app.include_router(endpoints.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
