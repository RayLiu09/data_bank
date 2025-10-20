# -*- coding: utf-8 -*-
import logging
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class DmClinicConcept(DBBase):
    __tablename__ = 'dm_clinic_concept'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="概念唯一标识")
    concept_code: Mapped[str] = Column(String(50), nullable=False, comment="概念编码, 如FGB, HbA1c")
    concept_name: Mapped[str] = Column(String(50), nullable=False, comment="概念名称, 如空腹血糖, 血糖")
    concept_type: Mapped[str] = Column(String(20), nullable=False, comment="概念类型, 如measure, procedure, diagnosis")
    unit: Mapped[str] = Column(String(20), nullable=True, comment="概念单位, 如mg/dL, mmol/L")
    normal_range_low: Mapped[float] = Column(Integer, nullable=True, comment="正常范围下限")
    normal_range_high: Mapped[float] = Column(Integer, nullable=True, comment="正常范围上限")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")