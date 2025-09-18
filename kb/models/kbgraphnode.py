from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KBGraphNodeBase(BaseModel):
    level_1: Optional[str] = Field(default="", description="知识图谱节点一级标签")
    level_2: Optional[str] = Field(default="", description="知识图谱节点二级标签")
    level_3: Optional[str] = Field(default="", description="知识图谱节点三级标签")
    level_4: Optional[str] = Field(default="", description="知识图谱节点四级标签")
    content: Optional[str] = Field(default="", description="知识图谱节点内容")
    kbgraph_id: Optional[int] = Field(default=None, gt=0, description="知识图谱ID")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")

    class Config:
        from_attributes = True
        model_config = {
            "from_attributes": True,
            "json_schema_extra": {
                "examples": [
                    {
                        "level_1": "level_1",
                        "level_2": "level_2",
                        "level_3": "level_3",
                        "level_4": "level_4",
                        "content": "content",
                        "kbgraph_id": 1,
                        "create_time": "2023-06-01T00:00:00"
                    }
                ]
            }
        }
    def to_dict(self):
        return self.model_dump(exclude_unset=True)

class KBGraphNodeCreate(KBGraphNodeBase):
    id: Optional[int]

class KBGraphNodeUpdate(KBGraphNodeBase):
    id: int

class KBGraphNode(KBGraphNodeBase):
    id: int

    def to_dict(self):
        return self.model_dump(exclude_unset=True)