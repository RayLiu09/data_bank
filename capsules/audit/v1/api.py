from fastapi import APIRouter

from settings import settings
from .endpoints import audit_ctl

audit_router = APIRouter()

audit_router.include_router(audit_ctl.router, prefix=f"/api/{settings.api_version}/audits", tags=["audits"])