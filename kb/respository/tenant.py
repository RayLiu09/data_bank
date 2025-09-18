from sqlalchemy.orm import Session

from kb.dbschema import Tenant
from kb.models.tenant import TenantCreate, TenantUpdate


class TenantRepository:
    def __init__(self):
        pass

    async def create_tenant(self, db: Session, tenant_in: TenantCreate) -> Tenant:
        db_tenant = Tenant(**tenant_in.to_dict())
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
        return db_tenant

    async def get_tenant(self, db: Session, tenant_id: int) -> Tenant:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()


    async def get_tenant_by_uuid(self, db: Session, uuid: str) -> Tenant:
        return db.query(Tenant).filter(Tenant.uuid == uuid).first()

    async def del_tenant(self, db: Session, tenant_id: int):
        db.query(Tenant).filter(Tenant.id == tenant_id).delete()

    async def update_tenant(self, db: Session, tenant_id: int, tenant_in: TenantUpdate) -> Tenant:
        db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        db_tenant.update(tenant_in.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(db_tenant)
        return db_tenant


tenant_repo = TenantRepository()