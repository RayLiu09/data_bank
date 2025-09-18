import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from capsules.authorization.schema import GrantPrivilege
from common.db_base import DBBase

class DataCapsule(DBBase):
    __tablename__ = "data_capsule"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="数据唯一标识")
    zkp: Mapped[dict] = Column(Text, comment="零知识证明数据")
    zkp_digest: Mapped[str] = Column(String(128), comment="零知识证明数据摘要")
    gene_data: Mapped[dict] = Column(Text, comment="基因数据")
    gene_data_digest: Mapped[str] = Column(String(128), comment="基因数据摘要")
    raw_data: Mapped[dict] = Column(Text, comment="原始数据")
    raw_data_digest: Mapped[str] = Column(String(128), comment="原始数据摘要")
    signature: Mapped[str] = Column(String(512), comment="RSA-2048签名")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")
    grants: Mapped[list[GrantPrivilege]] = relationship("GrantPrivilege", back_populates="capsule")
    aes_key_id: Mapped[int] = Column(Integer, ForeignKey("secret_key.id"), comment="AES-256密钥ID")
    aes_key = relationship("SecretKey", back_populates="capsules")

    def __repr__(self):
        return f"DataCapsule(id={self.id}, uuid={self.uuid}, zkp={self.zkp}, zkp_digest={self.zkp_digest}, gene_data={self.gene_data}, gene_data_digest={self.gene_data_digest}, raw_data={self.raw_data}, raw_data_digest={self.raw_data_digest}, signature={self.signature}, create_time={self.create_time})"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "zkp": self.zkp,
            "zkp_digest": self.zkp_digest,
            "gene_data": self.gene_data,
            "gene_data_digest": self.gene_data_digest,
            "raw_data": self.raw_data,
            "raw_data_digest": self.raw_data_digest,
            "signature": self.signature,
            "create_time": self.create_time
        }