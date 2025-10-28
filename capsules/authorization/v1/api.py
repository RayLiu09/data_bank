from fastapi import APIRouter

from settings import settings
from .endpoints import capsule_ctl, claim_ctl

capsule_api_router = APIRouter()

capsule_api_router.include_router(capsule_ctl.router, prefix=f"/api/{settings.api_version}/capsules", tags=["capsules"])
capsule_api_router.include_router(claim_ctl.router, prefix=f"/api/{settings.api_version}/claims", tags=["claims"])