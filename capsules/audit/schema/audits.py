import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class AuditLog(DBBase):
    __tablename__ = "audit_log"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="唯一标识")
    capsule_uuid: Mapped[str] = Column(String(36), comment="数据胶囊唯一标识")
    claim_uuid: Mapped[str] = Column(String(36), comment="授权记录唯一标识")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, uuid={self.uuid}, capsule_uuid={self.capsule_uuid}, grant_record_uuid={self.claim_uuid}, create_time={self.create_time})>"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "capsule_uuid": self.capsule_uuid,
            "claim_uuid": self.claim_uuid,
            "create_time": self.create_time
        }