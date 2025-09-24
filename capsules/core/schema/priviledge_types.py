import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class PrivilegeType(DBBase):
    """
    权限类型
    """
    __tablename__ = "privilege_type"

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="权限类型唯一标识")
    name: Mapped[str] = Column(String(36), comment="权限类型名称")
    description: Mapped[str] = Column(String(255), comment="权限类型描述")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")