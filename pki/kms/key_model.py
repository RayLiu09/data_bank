# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import BaseModel, Field


class KeyModel(BaseModel):
    """
    密钥模型
    """
    aes_key: str = Field(default= None, alias="aes_key", title="AES密钥", description="AES密钥")
    aes_operation_mode: str = Field(default= None, alias="aes_operation_mode", title="AES密钥的加密模式", description="AES密钥的加密模式")
    aes_iv: str = Field(default= None, alias="aes_iv", title="AES密钥的初始向量", description="AES密钥的初始向量")
    deprecated: bool = Field(default= False, alias="deprecated", title="是否弃用", description="是否弃用")
    create_time: datetime = Field(default= datetime.now(), alias="create_time", title="创建时间", description="创建时间")

class KeyModelView(KeyModel):
    """
    密钥模型视图
    """
    id: int = Field(alias="id", title="主键ID", description="主键ID")
    uuid: str = Field(alias="uuid", title="KEY唯一标识", description="KEY唯一标识")
