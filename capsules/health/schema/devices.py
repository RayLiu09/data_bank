# -*- coding: utf-8 -*-
import logging
import uuid
from datetime import datetime

from sqlalchemy import Integer, Column, String, Boolean, DateTime
from sqlalchemy.orm import Mapped

from common.db_base import DBBase


class Devices(DBBase):
    __tablename__ = 'devices'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = Column(Integer, autoincrement=True, primary_key=True, index=True, comment="主键ID")
    uuid: Mapped[str] = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False, comment="设备唯一标识")
    owner: Mapped[str] = Column(String(36), nullable=False, comment="设备所属者")
    type: Mapped[str] = Column(String(20), nullable=False, comment="设备类型, 如watch, scale, bp_monitor")
    model: Mapped[str] = Column(String(50), nullable=False, comment="设备型号")
    manufacturer: Mapped[str] = Column(String(50), nullable=False, comment="设备制造商")
    firmware_version: Mapped[str] = Column(String(20), nullable=False, comment="设备固件版本")
    mac_address: Mapped[str] = Column(String(20), nullable=False, comment="设备MAC地址")
    serial_number: Mapped[str] = Column(String(20), nullable=False, comment="设备序列号")
    is_active: Mapped[bool] = Column(Boolean, default=True, comment="设备是否激活")
    registered_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="设备注册时间")
    last_active_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="设备最后活跃时间")
    last_sync_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="设备最后同步时间")
    create_time: Mapped[datetime] = Column(DateTime, default=datetime.now, comment="设备创建时间")