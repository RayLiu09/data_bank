from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class TenantBase(BaseModel):
    """租户表的BaseModel"""
    name: str
    domain: str
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    default_model_provider: Optional[str] = None
    create_time: Optional[datetime] = None
    uuid: Optional[str] = None
    def to_dict(self):
        return self.model_dump(exclude_unset=True)

class TenantCreate(TenantBase):
    """租户表的CreateModel"""
    id: Optional[int] = None

class TenantUpdate(TenantBase):
    """租户表的UpdateModel"""
    pass

class Tenant(TenantBase):
    """租户表的InDBBaseModel"""
    id: Optional[int] = None

    def to_dict(self):
        return self.model_dump(exclude_unset=True)

