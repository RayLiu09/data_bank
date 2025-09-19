import uuid
from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, JSON
from sqlalchemy.orm import Mapped, relationship

from capsules.core.schema import DataCapsule
from common.db_base import DBBase


class CapsuleAdditionalProps(DBBase):
    __tablename__ = "capsule_additional_props"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="数据唯一标识")
    type: Mapped[str] = Column(String(5), comment="胶囊数据类型，如10001-CT报告")
    owner: Mapped[str] = Column(String(36), comment="胶囊拥有者")
    # 采集者标识
    collector: Mapped[str] = Column(String(36), comment="胶囊采集者")
    sexy: Mapped[int] = Column(Integer, comment="性别")
    age: Mapped[int] = Column(Integer, comment="年龄")
    area: Mapped[dict] = Column(JSON, comment="地区")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")
    capsules: Mapped[list[DataCapsule]] = relationship("DataCapsule", back_populates="additional_props")