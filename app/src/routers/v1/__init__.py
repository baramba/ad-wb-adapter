from routers.v1 import campaigns, jobs
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")
router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
