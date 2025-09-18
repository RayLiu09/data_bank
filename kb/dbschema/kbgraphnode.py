import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey,Column
from sqlalchemy.orm import  Mapped, relationship

from common.db_base import DBBase


class KBGraphNode(DBBase):
    __tablename__ = "kb_graph_node"

    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="唯一标识")
    level_1: Mapped[Optional[str]] = Column(String(200), comment="章名称")
    level_2: Mapped[Optional[str]] = Column(String(200), comment="节名称")
    level_3: Mapped[Optional[str]] = Column(String(200), comment="小节名称")
    level_4: Mapped[Optional[str]] = Column(String(200), comment="知识点名称")
    content: Mapped[Optional[str]] =  Column(Text, comment="知识点内容")
    create_time: Mapped[Optional[DateTime]] = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    id: Mapped[int] = Column(Integer, autoincrement=True,primary_key=True, index=True, comment="主键ID")
    kbgraph_id: Mapped[int] = Column(Integer, ForeignKey("kb_graph.id"), comment="知识图谱ID")
    kbgraph = relationship("KBGraph", back_populates="nodes")

    def __repr__(self):
        return "<KBGraphNode(id='%s', level_1='%s', level_2='%s', level_3='%s', level_4='%s', content='%s', create_time='%s')>" % (self.id, self.level_1, self.level_2, self.level_3, self.level_4, self.content, self.create_time)

    def to_dict(self):
        """将实体类转换为字典"""
        return {
            "id": self.id,
            "kbgraph_id": self.kbgraph_id,
            "level_1": self.level_1,
            "level_2": self.level_2,
            "level_3": self.level_3,
            "level_4": self.level_4,
            "content": self.content,
            "create_time": self.create_time
        }