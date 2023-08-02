from fastapi import APIRouter

from routers.v1 import advert, campaign, jobs, product, supplier

router = APIRouter(prefix="/v1")
router.include_router(campaign.router)
router.include_router(jobs.router)
router.include_router(supplier.router)
router.include_router(advert.router)
router.include_router(product.router)
