#- *- coding: utf-8 -
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped
from common.db_base import DBBase

class DmChronicDisease(DBBase):
    __tablename__ = 'dm_chronic_disease'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="疾病唯一标识")
    disease_name: Mapped[str] = Column(String(50), nullable=False, comment="慢性疾病名称， 如高血压，2型糖尿病等")
    diagnosis_time: Mapped[datetime] = Column(DateTime, nullable=False, comment="疾病诊断时间")
    risk_level: Mapped[int] = Column(Integer, nullable=False, comment="疾病风险等级， 1-5级")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="创建时间")