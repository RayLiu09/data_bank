from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KBGraphBase(BaseModel):
    name: str = Field(..., description="知识图谱名称")
    group: str = Field(..., description="知识图谱分组")
    description: Optional[str] = Field(default="", description="知识图谱描述")
    tenant_id: Optional[int] = Field(default=None, gt=0, description="租户ID")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")

    class Config:
        model_config = {
            "from_attributes": True,
            "json_schema_extra": {
                "examples": {
                    "name": "知识图谱名称",
                    "group": "知识图谱分组",
                    "description": "知识图谱描述",
                    "tenant_id": 1,
                    "create_time": "2023-01-01 00:00:00"
                }
            }
        }

class KBGraphCreate(KBGraphBase):
    id: Optional[int]

class KBGraphUpdate(KBGraphBase):
    pass

class KBGraph(KBGraphBase):
    id: int

    class Config:
        from_attributes = True

    def to_dict(self):
        return self.model_dump(exclude_unset=True)