import logging
from datetime import timedelta, datetime

from fastapi import APIRouter
from fastapi.params import Form, Header
from starlette import status

from common.db_deps import SessionDep
from common.response_util import response_base
from security.access_token import create_access_token
from security.acl_repo import AclControlCreate, acl_control_repo
from settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ak_sk", summary="Create a new acl control")
async def create_ak_sk(db: SessionDep, acl_control_in: AclControlCreate):
    acl_control = await acl_control_repo.create_acl_control(db, acl_control_in)
    logger.info("Created acl control: %s", acl_control)
    return {"code": status.HTTP_200_OK, "msg": "Create AK/SK successfully", "data": {"acl_key": acl_control.acl_key, "acl_secret": acl_control.acl_secret}}

@router.post("/access_token", summary="Generate an access token")
async def get_access_token(db: SessionDep, tenant_uuid: str = Header(...), acl_key: str = Form(default="all"), acl_secret: str = Form(...)):
    """
    Generate an access token
    """
    if tenant_uuid is None or acl_secret is None:
        return await response_base.fail(code=400, msg="Invalid parameters", data=None)
    if acl_key is None:
        acl_key = "all"

    is_valid = await acl_control_repo.is_acl_control_valid(db, acl_key, acl_secret, tenant_uuid)
    if not is_valid:
        return await response_base.fail(code=400, msg="Acl secret key is expired", data=None)
    access_token = create_access_token(data={"sub": {"tenant_uuid": tenant_uuid, "acl_key":acl_key, "acl_secret":acl_secret }}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    logger.info("Generated access token: %s", access_token)
    return await response_base.success_simple(data={"access_token": access_token, "token_type": "bearer", "expires_in": datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)})