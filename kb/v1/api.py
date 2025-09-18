from fastapi import APIRouter

from settings import settings
from .endpoints import kbgrah, tenant

kb_api_router = APIRouter()

kb_api_router.include_router(kbgrah.router, prefix=f"/api/{settings.api_version}/kbgraph", tags=["kbgrah"])
kb_api_router.include_router(tenant.router, prefix=f"/api/{settings.api_version}/tenant", tags=["tenant"])