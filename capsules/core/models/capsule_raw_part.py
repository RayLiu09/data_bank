from typing import Optional

from pydantic import BaseModel, Field


class HenTimestamp(BaseModel):
    timestamp: int = Field(..., description="时间戳")
    signature: Optional[str] = Field(..., description="可确认签名")

class CapsuleRawPart(BaseModel):
    # 数据生成时间戳
    gen_timestamp: HenTimestamp = Field(..., description="数据生成时间戳")
    # 数据生成单位
    gen_agent: str = Field(default= None, description="数据生成单位")
    # 报告单内容
    data: dict = Field(default= None, description="报告单内容")

    class Config:
        schema_extra = {
            "example": {
                "gen_timestamp": {
                    "timestamp": 1680000000,
                    "signature": "1234567890"
                },
                "gen_agent": "上海健康科技有限公司",
                "data": {
                    "血液检查": [
                        {
                            "指标名": "白细胞计数",
                            "指标值": 6.5,
                            "范围下限": 4.0,
                            "范围上限": 10.0,
                            "单位": "个/升",
                            "参考值": "4.0-10.0"
                        },
                        {
                            "指标名": "红细胞计数",
                            "指标值": 4.5,
                            "范围下限": 4.0,
                            "范围上限": 10.0,
                            "单位": "个/升",
                            "参考值": "4.0-10.0"
                        }
                    ],
                    "B超检查": [
                        {
                            "器官名": "肝脏",
                            "测量值": "回声增强",
                            "状态评价": "符合脂肪浸润表现"
                        },
                        {
                            "器官名": "脾脏",
                            "测量值": "正常",
                            "状态评价": "未见异常"
                        },
                        {
                            "器官名": "肾脏",
                            "测量值": "正常",
                            "状态评价": "未见异常"
                        }
                    ]
                }
            }
        }