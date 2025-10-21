import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship

from common.db_base import DBBase


class CapsuleClaim(DBBase):
    __tablename__ = "capsule_claims"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="权限唯一标识")
    one_time_use: Mapped[bool] = Column(Boolean, default=False, comment="是否一次性使用")
    expires_at: Mapped[Optional[DateTime]] = Column(DateTime, nullable=True, comment="权限到期时间")
    deprecated: Mapped[bool] = Column(Boolean, default=False, comment="是否弃用")
    authorizer: Mapped[str] = Column(String(36), comment="授权者")
    authorizer_signature: Mapped[str] = Column(String(255), comment="授权者签名")
    receiver: Mapped[str] = Column(String(36), comment="接收者")
    capsules: Mapped[List[str]] = Column(Text, comment="数据胶囊唯一标识")
    privacy_level: Mapped[int] = Column(Integer, comment="隐私等级")
    scope: Mapped[str] = Column(Text, nullable=True, comment="数据范围")
    type: Mapped[str] = Column(String(5), nullable=True,
                               comment="权限类型, 1-修改权，2-解释权，3-所有权, 4-使用权, 5-装让权, 6-阅读权,7-是否可追溯,8-预留, 其中4使用权可分4-1: 无限制，4-2: 不可多条件统计，4-3-1: 可看可用,4-3-2:可看不可用, 4-3-3:不可看可用")
    create_time: Mapped[DateTime] = Column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<CapsuleClaim(id={self.id}, uuid={self.uuid}, type={self.type}, one_time_use={self.one_time_use}, expires_at={self.expires_at}, deprecated={self.deprecated}, create_time={self.create_time})>"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "type": self.type,
            "one_time_use": self.one_time_use,
            "expires_at": self.expires_at,
            "deprecated": self.deprecated,
            "create_time": self.create_time
        }
