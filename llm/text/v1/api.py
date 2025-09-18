from fastapi import APIRouter

from llm.text.v1.endpoints import contents
from settings import settings

text_api_router = APIRouter()

text_api_router.include_router(contents.router, prefix=f"/api/{settings.api_version}/contents", tags=["contents"])