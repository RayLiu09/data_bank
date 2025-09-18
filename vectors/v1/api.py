from fastapi import APIRouter

from settings import settings
from vectors.v1.endpoints import vectors

vector_api_router = APIRouter()

vector_api_router.include_router(vectors.router, prefix=f"/api/{settings.api_version}/vectors", tags=["vectors"])
