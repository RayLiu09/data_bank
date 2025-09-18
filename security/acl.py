from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from common.db_base import DBBase


class AclControl(DBBase):
    __tablename__ = "acl_control"

    acl_key: Mapped[str] = mapped_column(String(50), default="all", nullable=False, comment="权限标识")
    acl_secret: Mapped[str] = mapped_column(String(50), nullable=False, comment="权限密钥")
    expire_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    tenant_uuid: Mapped[str] = mapped_column(String(36), nullable=False, comment="租户唯一标识")
    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment="主键ID")
