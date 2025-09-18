import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Column, Integer
from sqlalchemy.orm import Mapped, relationship

from common.db_base import DBBase


class KBGraph(DBBase):
    __tablename__ = "kb_graph"

    uuid: Mapped[str] = Column(String(36), unique=True,default=lambda: str(uuid.uuid4()), nullable=False, comment="唯一标识")
    name: Mapped[str] = Column(String(200), nullable=False, comment="知识库名称")
    group: Mapped[str] = Column(String(50), nullable=False, comment="知识库分组")
    description: Mapped[Optional[str]] = Column(String(500), comment="知识描述")
    create_time: Mapped[Optional[DateTime]] = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    id: Mapped[int] = Column(Integer, autoincrement=True,primary_key=True, index=True, comment="主键ID")
    tenant_id: Mapped[int] = Column(ForeignKey("tenant.id"), nullable=True, comment="租户ID")
    nodes = relationship("KBGraphNode", back_populates="kbgraph")

    def __repr__(self):
        return f"KBGraph(name={self.name}, group={self.group}, description={self.description}, create_time={self.create_time}, id={self.id}, tenant_id={self.tenant_id})"

    def to_dict(self):
        return {
            "name": self.name,
            "group": self.group,
            "description": self.description,
            "create_time": self.create_time,
            "id": self.id,
            "tenant_id": self.tenant_id
        }
