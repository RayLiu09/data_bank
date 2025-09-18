import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, ForeignKey, String, DateTime,Column
from sqlalchemy.orm import  Mapped

from common.db_base import DBBase


class KBGraphEdge(DBBase):
    __tablename__ = "kb_graph_edge"

    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="唯一标识")
    source: Mapped[int] = Column(Integer, ForeignKey("kb_graph_node.id"), nullable=False, comment="源节点ID")
    target: Mapped[int] = Column(Integer, ForeignKey("kb_graph_node.id"), nullable=False, comment="目标节点ID")
    relation_type: Mapped[str] = Column(String(50), nullable=False, comment="关系类型")
    order: Mapped[int] = Column(Integer, nullable=False, comment="顺序")
    create_time: Mapped[Optional[DateTime]] = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    id: Mapped[int] = Column(Integer, autoincrement=True,primary_key=True, index=True, comment="主键ID")

    def __repr__(self):
        return f"KBGraphEdge(source={self.source}, target={self.target}, relation_type={self.relation_type}, order={self.order}, create_time={self.create_time}, id={self.id})"

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "order": self.order,
            "create_time": self.create_time,
            "id": self.id
        }