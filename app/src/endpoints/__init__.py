from endpoints import v1
from fastapi import APIRouter

router = r = APIRouter(prefix='/api')

r.include_router(v1.router)
