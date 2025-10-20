from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from common.db_base import DBBase


class CapsuleOwner(DBBase):
    __tablename__ = "capsule_owner"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="自增ID")
    owner_uuid: str = Column(String(36), comment="数据胶囊所有者UUID")
    capsule_uuid: str = Column(String(36), comment="数据胶囊UUID")
    create_time: datetime = Column(DateTime, default=datetime.now, comment="创建时间")