from fastapi import APIRouter

from core.settings import settings
from routers.v1 import campaign, jobs, product, stake, supplier

router = APIRouter(prefix=f"{settings.CONTEXT}/v1")
router.include_router(campaign.router)
router.include_router(jobs.router)
router.include_router(supplier.router)
router.include_router(stake.router)
router.include_router(product.router)
