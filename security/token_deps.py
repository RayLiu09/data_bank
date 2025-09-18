import logging

import jwt
from fastapi import Depends
from fastapi.params import Header
from jwt import DecodeError, ExpiredSignatureError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from common.db_deps import SessionDep
from common.response_util import response_base
from security.acl_repo import acl_control_repo
from settings import settings

logger = logging.getLogger(__name__)


async def is_token_valid(db: SessionDep, tenant_uuid: str = Header(..., description="租户唯一标识"),
                         token: str = Header(..., description="验证Token有效性")):
    unauthorized_exception = HTTPException(status_code=401, detail="token验证失败", headers={"WWW-Authenticate": "Bearer"})
    try:
        if not tenant_uuid:
            logger.warning("Not include the tenant uuid in request header.")
        encoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        sub = encoded_data.get("sub")
        if sub:
            tenant_uuid = sub.get("tenant_uuid")
            acl_key = sub.get("acl_key")
            acl_secret = sub.get("acl_secret")
            if await acl_control_repo.is_acl_control_valid(db, acl_key, acl_secret, tenant_uuid):
                return response_base.success_simple(data={"tenant_uuid": tenant_uuid, "acl_key": acl_key, "acl_secret": acl_secret})
            else:
                raise unauthorized_exception
    except DecodeError:
        raise unauthorized_exception
    except ExpiredSignatureError:
        raise unauthorized_exception
    except Exception as e:
        raise unauthorized_exception

TokenDeps = Depends(is_token_valid)