# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CapsuleScope(BaseModel):
    basic_data: List[str] = Field(default=[], description="基础数据维度")
    zkp_data: List[str] = Field(default=[], description="ZKP数据指标")


class CapsuleClaimModel(BaseModel):
    capsules: List[str] = Field(..., description="数据胶囊UUID列表")
    authorizer: str = Field(..., description="授权者UUID")
    receiver: str = Field(..., description="接收者UUID")
    privacy_level: int = Field(int(0), ge=0, le=4, description="隐私等级")
    scope: CapsuleScope = Field(default=None, description="数据范围")
    one_time_use: bool = Field(default=False, description="是否一次性授权")
    expires_at: datetime = Field(default=None, description="数据胶囊有效期")