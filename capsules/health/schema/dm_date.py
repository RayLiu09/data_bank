# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class DmDate(DBBase):
    __tablename__ = "dm_date"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="数据唯一标识")
    day_of_week: Mapped[int] = Column(Integer, nullable=False, comment="星期几")
    is_weekend: Mapped[bool] = Column(Boolean, nullable=False, comment="是否周末")
    day_of_month: Mapped[int] = Column(Integer, nullable=False, comment="月份的第几天")
    month: Mapped[int] = Column(Integer, nullable=False, comment="月份")
    year: Mapped[int] = Column(Integer, nullable=False, comment="年份")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")