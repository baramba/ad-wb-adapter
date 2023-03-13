from fastapi import APIRouter

from endpoints.v1.get import base

router = r = APIRouter()

r.include_router(base.router)