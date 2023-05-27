from routers.v1 import campaign, jobs, supplier, stake
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")
router.include_router(campaign.router)
router.include_router(jobs.router)
router.include_router(supplier.router)
router.include_router(stake.router)
