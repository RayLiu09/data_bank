from datetime import datetime

import uuid
from typing import Optional

from sqlalchemy import String, DateTime, Column, Integer
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class Tenant(DBBase):
    __tablename__ = "tenant"

    uuid: Mapped[Optional[str]] = Column(String(36), default=lambda: str(uuid.uuid4()), comment="租户UUID")
    name = Column(String(50), nullable=False, comment="租户名称")
    domain = Column(String(50), nullable=True, comment="租户域名")
    address = Column(String(255), nullable=True, comment="租户地址")
    phone = Column(String(20), nullable=True, comment="租户电话")
    description = Column(String(500), nullable=True, comment="租户描述")
    default_model_provider = Column(String(50), default="openai", comment="默认模型供应商")
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")

    def __repr__(self):
        return f"<Tenant(name={self.name}, domain={self.domain})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
