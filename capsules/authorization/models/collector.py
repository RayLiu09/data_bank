from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field


class CollectorPropModel(BaseModel):
    """
    Collect 0-level data capsule from app side
    """
    type: Optional[str] = Field(..., description="数据胶囊类型")
    owner: Optional[str] = Field(..., description="数据胶囊拥有者")
    collector: Optional[str] = Field(..., description="数据胶囊采集者")
    age: Optional[int] = Field(default=0, description="数据胶囊拥有者年龄")
    area: Optional[dict] = Field(default=None, description="数据胶囊拥有者所在地区")
    sexy: Optional[int] = Field(default=0, description="数据胶囊拥有者性别")
