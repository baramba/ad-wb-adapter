from fastapi import APIRouter
from endpoints.v1 import get, request

router = r = APIRouter(prefix='/v1')

r.include_router(get.router)
r.include_router(request.router)
