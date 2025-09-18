from fastapi import APIRouter

from settings import settings
from .endpoints import acl_controller

access_token_router = APIRouter()

access_token_router.include_router(acl_controller.router, prefix=f"/api/{settings.api_version}/acl", tags=["acl"])