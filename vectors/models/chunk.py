from datetime import datetime

from pydantic import BaseModel


class Chunk(BaseModel):
    doc_name: str
    content: str
    chunk_id: int
    doc_uuid: str = ''
    tokens: int = 0
    vector: list = None
    metadata: dict = None
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
