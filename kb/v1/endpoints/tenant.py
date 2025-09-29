import logging

from fastapi import APIRouter, Header

from common.db_deps import SessionDep
from common.response_util import response_base
from kb.models.tenant import Tenant, TenantCreate, TenantUpdate
from kb.respository.tenant import tenant_repo
from security.token_deps import TokenDeps

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("", response_model=Tenant, dependencies=[TokenDeps], summary="Fetch tenant by id")
async def get_tenant(db: SessionDep, tenant_uuid: str = Header(..., description="租户唯一标识")) -> Tenant:
    """
    Fetch tenant by id
    """
    logger.info("Fetch tenant by id: %s", tenant_uuid)
    if tenant_uuid is None:
        return response_base.fail(code=400, msg="参数错误")
    return await tenant_repo.get_tenant_by_uuid(db, tenant_uuid)

@router.post("/", response_model=Tenant, summary="Create a tenant")
async def create_tenant(db: SessionDep, tenant_in: TenantCreate) -> Tenant:
    """
    Create a tenant
    :param db:
    :param tenant_in:
    :return:
    """
    return await tenant_repo.create_tenant(db, tenant_in=tenant_in)

@router.put("/{tenant_id}", response_model=Tenant, summary="Update tenant")
async def update_tenant(db: SessionDep, tenant_id: int, tenant_in: TenantUpdate) -> Tenant:
    """
    Update tenant
    :param db:
    :param tenant_id:
    :param tenant_in:
    :return:
    """
    return await tenant_repo.update_tenant(db, tenant_id, tenant_in)
