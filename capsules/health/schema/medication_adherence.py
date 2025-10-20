# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

from sqlalchemy import Integer, Column, String, DOUBLE, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class MedicationAdherence(DBBase):
    __tablename__ = 'medication_adherence'

    # 用药遵从性记录表
    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="用药遵从性记录唯一标识")
    owner: Mapped[str] = Column(String(36), nullable=False, comment="数据所属者")
    medication_name: Mapped[str] = Column(String(50), nullable=False, comment="用药名称")
    prescribed_dosage: Mapped[float] = Column(DOUBLE, nullable=False, comment="用药剂量")
    was_taken: Mapped[bool] = Column(Boolean, nullable=False, comment="是否已take")
    scheduled_time: Mapped[datetime] = Column(DateTime, nullable=False, comment="用药计划时间")
    actual_time: Mapped[datetime] = Column(DateTime, nullable=True, comment="实际用药时间")
    chronic_disease_id: Mapped[int] = Column(Integer, ForeignKey("dm_chronic_disease.id"), nullable=False, comment="疾病ID")
    date_id: Mapped[int] = Column(Integer, ForeignKey("dm_date.id"), nullable=False, comment="日期ID")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")
