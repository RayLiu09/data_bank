import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from security.acl import AclControl
logger = logging.getLogger(__name__)

class AclControlCreate(BaseModel):
    tenant_uuid: str
    acl_key: Optional[str] = "all"
    expire_time: Optional[datetime] = datetime.now() + timedelta(days=30)
    create_time: Optional[datetime] = datetime.now()

class AclControlModel(AclControlCreate):
    id: int
    acl_key: str
    acl_secret: str
    create_time: datetime
    expire_time: datetime
    tenant_uuid: str


class AclControlRepository:
    def __init__(self):
        pass

    async def create_acl_control(self, db: Session, acl_control_in: AclControlCreate) -> AclControl:
        db_acl_control = AclControl(**acl_control_in.model_dump(exclude_unset=True), acl_secret=uuid.uuid4().hex)
        db.add(db_acl_control)
        db.commit()
        db.refresh(db_acl_control)
        print(f"**************{acl_control_in}************")
        return db_acl_control

    async def is_acl_control_valid(self, db: Session, acl_key: str, acl_secret: str, tenant_uuid: str) -> bool:
        acl_control = db.query(AclControl).filter(AclControl.acl_key == acl_key,
                                                  AclControl.acl_secret == acl_secret,
                                                  AclControl.tenant_uuid == tenant_uuid).first()
        logger.info(f"**************{acl_control}************")
        if acl_control and acl_control.expire_time > datetime.now():
            return True
        else:
            return False

acl_control_repo = AclControlRepository()