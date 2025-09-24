import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, relationship

from common.db_base import DBBase


class SecretKey(DBBase):
    __tablename__ = "secret_key"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="KEY唯一标识")
    aes_key: Mapped[str] = Column(String(64), nullable=False, comment="Base64编码的AES-256密钥")
    aes_operation_mode: Mapped[str] = Column(String(16), nullable=False, default="CBC", comment="AES密钥的加密模式")
    aes_iv: Mapped[str] = Column(String(64), nullable=False, comment="AES密钥的初始向量")
    deprecated: Mapped[bool] = Column(Boolean, default=False, comment="是否弃用")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")
    capsules = relationship("DataCapsule", back_populates="aes_key")

    def __repr__(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "aes_key": self.aes_key,
            "aes_operation_mode": self.aes_operation_mode,
            "aes_iv": self.aes_iv,
            "deprecated": self.deprecated,
            "create_time": self.create_time
        }