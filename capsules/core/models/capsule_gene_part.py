from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CapsuleGenePart(BaseModel):
    collector_agent: str = Field(..., description="数据采集机构")
    collector_time: datetime = Field(..., description="数据采集时间")
    customer: str = Field(..., description="数据所属客户")
    data_type: str = Field(..., description="数据类型")
    doctor: str = Field(..., description="开单医生")
    doctor_time: Optional[datetime] = Field(..., description="开单时间")
    # 执行医生
    execute_doctor: Optional[str] = Field(None, description="执行医生")
    execute_time: Optional[datetime] = Field(None, description="执行时间")
    # 执行部门
    execute_department: Optional[str] = Field(None, description="执行部门")