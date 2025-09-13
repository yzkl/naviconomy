from fastapi import APIRouter

from . import brands, octanes, refills

base_router = APIRouter()

base_router.include_router(brands.router, prefix="/v1", tags=["Brands"])
base_router.include_router(octanes.router, prefix="/v1", tags=["Octanes"])
base_router.include_router(refills.router, prefix="/v1", tags=["Refills"])
