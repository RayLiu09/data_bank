# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import DateTime, Column, String, DOUBLE, SMALLINT, Text, PrimaryKeyConstraint, Index, Integer, \
    ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class HealthMetrics(DBBase):
    __tablename__ = 'health_metrics'
    # 定义联合主键
    __table_args__ = (
        PrimaryKeyConstraint('time', 'owner', 'device_uuid'),
        # 定义索引
        Index('idx_owner_time', 'owner', 'time')
    )

    # 时间序列字段, time, timestamp
    time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="时间")
    owner: Mapped[str] = Column(String(36), nullable=False, comment="数据所属者")
    device_uuid: Mapped[str] = Column(String(36), nullable=False, comment="数据所属设备")
    metric_value: Mapped[float] = Column(DOUBLE, nullable=False, comment="数据值")
    quality_score: Mapped[int] = Column(SMALLINT, nullable=False, comment="数据质量得分, 0 ~ 100")
    raw_data_ciphertext: Mapped[str] = Column(Text, nullable=False, comment="原始数据, JSON类型")
    chronic_disease_id: Mapped[int] = Column(Integer, ForeignKey("dm_chronic_disease.id"), nullable=False, comment="疾病ID")
    clinical_concept_id: Mapped[int] = Column(Integer, ForeignKey("dm_clinic_concept.id"), nullable=False, comment="临床概念ID")
    date_id: Mapped[int] = Column(Integer, ForeignKey("dm_date.id"), nullable=False, comment="日期ID")
    secret_id: Mapped[int] = Column(Integer, ForeignKey("secret_key.id"), nullable=False, comment="密钥ID")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="数据创建时间")

