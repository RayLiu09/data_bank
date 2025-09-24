from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class DataCapsuleModel(BaseModel):
    """
    数据胶囊模型
    """
    summary_data: Optional[str] = Field(..., description="概要数据")
    gene_data: Optional[dict] = Field(..., description="基因数据")
    raw_data: Optional[dict] = Field(..., description="原始数据")
    signature: Optional[str] = Field(..., description="RSA-2048签名")
    additional_props: Optional[dict] = Field(..., description="元数据,明文存储用于1阶胶囊检索支撑")

class DataCapsuleModelView(DataCapsuleModel):
    """
    数据胶囊模型视图
    """
    id: Optional[int] = Field(..., description="数据胶囊ID")
    uuid: Optional[str] = Field(..., description="数据唯一标识")
    create_time: Optional[datetime] = Field(default=datetime.now, description="创建时间")

    class Config:
        orm_mode = True
        example = {
            "id": 1,
            "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "create_time": "2025-01-01 00:00:00",
            "summary_data": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "gene_data": {
                "collector_agent": "xxx三甲医院检测中心",
                "collector_time": "2025-01-01 00:00:00",
                "customer": "张三",
                "gene_type": "基因检测",
                # 开方医生
                "doctor": "李医生",
                "docter_time": "2025-01-01 00:00:00",
                # 检测执行人员
                "executor": "王医生",
                "executor_time": "2025-01-01 00:00:00",
                # 科室名称
                "executor_department": " Bioinformatics",
            },
            "raw_data": {},
            "signature": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "additional_props": {
                "age": 18,
                "area": {
                    "province": "北京",
                    "city": "北京",
                    "district": "北京",
                },
                "collector": "550e8400-e29b-41d4-a716-446655440000",
                "owner": "550e8400-e29b-41d4-a716-446655440000",
                "sexy": 1,
                "type": "10001",
            },
        }