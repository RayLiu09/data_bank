from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KBGraphEdgeBase(BaseModel):
    source: int
    target: int
    relation_type: str
    order: Optional[int]
    create_time: Optional[datetime]

    def to_dict(self):
        return self.model_dump(exclude_unset=True)

class KBGraphEdgeCreate(KBGraphEdgeBase):
    pass

class KBGraphEdgeUpdate(KBGraphEdgeBase):
    id: int

class KBGraphEdge(KBGraphEdgeBase):
    id: int

    def to_dict(self):
        return self.model_dump(exclude_unset=True)