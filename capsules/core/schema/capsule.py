import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from capsules.authorization.schema import CapsuleClaim
from common.db_base import DBBase

class DataCapsule(DBBase):
    __tablename__ = "capsules"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="数据唯一标识")
    # 概要数据
    summary_ciphertext: Mapped[dict] = Column(Text, comment="数据胶囊的概要数据")
    gene_ciphertext: Mapped[dict] = Column(Text, comment="基因数据")
    raw_ciphertext: Mapped[dict] = Column(Text, comment="原始数据")
    signature: Mapped[str] = Column(String(2048), comment="RSA-2048签名")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")
    claims: Mapped[list[CapsuleClaim]] = relationship("CapsuleClaim", back_populates="capsule")
    aes_key_id: Mapped[int] = Column(Integer, ForeignKey("secret_key.id"), comment="AES-256密钥ID")
    aes_key = relationship("SecretKey", back_populates="capsules")
    additional_props_id: Mapped[int] = Column(Integer, ForeignKey("capsule_additional_props.id"), comment="附加属性ID")
    additional_props = relationship("CapsuleAdditionalProps", back_populates="capsules")

    def __repr__(self):
        return f"DataCapsule(id={self.id}, uuid={self.uuid}, summary_data={self.summary_ciphertext}, gene_data={self.gene_ciphertext}, raw_data={self.raw_ciphertext}, signature={self.signature}, create_time={self.create_time})"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "zkp_data": self.summary_ciphertext,
            "gene_data": self.gene_ciphertext,
            "raw_data": self.raw_ciphertext,
            "signature": self.signature,
            "create_time": self.create_time
        }