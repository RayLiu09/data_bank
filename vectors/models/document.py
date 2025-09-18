from datetime import datetime

from pydantic import BaseModel

from vectors.models.chunk import Chunk


class Document(BaseModel):
    name: str = ''
    ext: str = ''
    content: str = ''
    chunks: list[Chunk] = []
    metadata: dict = None
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
