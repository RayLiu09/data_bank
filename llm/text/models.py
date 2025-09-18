from typing import Optional

from pydantic import BaseModel

from llm.model_provider.options import TuneDirection


class ContentPayload(BaseModel):
    subject: str
    style: str
    number: Optional[int] = 150

class TitlePayload(BaseModel):
    subject: str
    number: int

class ContextActionPayload(BaseModel):
    action: TuneDirection
    context: str
    prompt: str

class EcommercePayload(BaseModel):
    background: str
    subject: str
    number: Optional[int] = 150