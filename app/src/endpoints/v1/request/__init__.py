from fastapi import APIRouter

from endpoints.v1.request import campaign

router = r = APIRouter()

r.include_router(campaign.router)
