from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CapsuleAdditionalPropsModel(BaseModel):
    """
    Data capsule's additional props for analysis/statistics
    """
    type: str = Field(..., description="Capsule类型")
    owner: str = Field(..., description="Capsule拥有者")
    producer: Optional[str] = Field(..., description="Capsule采集者")
    producer_time: Optional[datetime] = Field(..., description="Capsule采集时间")
    level: Optional[int] = Field(1, description="Capsule阶数")
    sexy: Optional[int] = Field(..., description="Capsule拥有者性别")
    age: Optional[int] = Field(..., description="Capsule拥有者年龄")
    area: Optional[dict] = Field(..., description="Capsule拥有者所在地区")

class CapsuleAdditionalPropsView(CapsuleAdditionalPropsModel):
    """
    Data capsule's additional props for analysis/statistics
    """
    id: int = Field(..., description="Capsule附加属性ID")
    uuid: str = Field(..., description="Capsule数据唯一标识")
    create_time: datetime = Field(..., description="Capsule附加属性创建时间")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "type": "10001",
                "owner": "550e8400-e29b-41d4-a716-446655440000",
                "producer": "550e8400-e29b-41d4-a716-446655440235",
                "producer_time": "2021-01-01 00:00:00",
                "level": 1,
                "sexy": "1",
                "age": 1,
                "area": {"province": "1", "city": "1"},
                "uuid": "1",
                "create_time": "2021-01-01 00:00:00"
            }
        }
