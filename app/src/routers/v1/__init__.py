from routers.v1 import campaigns, jobs, supplier
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")
router.include_router(campaigns.router)
router.include_router(jobs.router)
router.include_router(supplier.router)
