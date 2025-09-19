from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field


class CollectorPropModel(BaseModel):
    """
    Collect 0-level data capsule from app side
    """
    type: str = Field(..., description="数据胶囊类型")
    owner: str = Field(..., description="数据胶囊拥有者")
    collector: str = Field(..., description="数据胶囊采集者")
    age: Optional[int] = Field(..., description="数据胶囊拥有者年龄")
    area: Optional[dict] = Field(..., description="数据胶囊拥有者所在地区")
    sexy: Optional[int] = Field(..., description="数据胶囊拥有者性别")
