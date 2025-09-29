import logging
from datetime import datetime

import jwt
from fastapi import Depends
from fastapi.params import Header
from jwt import DecodeError, ExpiredSignatureError
from starlette.exceptions import HTTPException

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
        logger.info(f"Verify token: {token}")

        # 尝试解码JWT token，不验证签名（用于调试）
        # 首先不验证签名来检查token结构
        # try:
        #     unverified_payload = jwt.decode(token, options={"verify_signature": False})
        #     logger.debug(f"Unverified token payload: {unverified_payload}")
        # except Exception as e:
        #     logger.error(f"Invalid token format: {str(e)}")
        #     raise unauthorized_exception

        # 正常验证签名和解码
        encoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = encoded_data.get("sub")
        if sub:
            # 检查sub是否为字符串，如果是则尝试解析为JSON
            if isinstance(sub, str):
                import json
                try:
                    sub = json.loads(sub)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse sub as JSON")
                    sub = {"tenant_uuid": tenant_uuid, "acl_key": None, "acl_secret": None}
            
            tenant_uuid = sub.get("tenant_uuid") if sub.get("tenant_uuid") else tenant_uuid
            acl_key = sub.get("acl_key")
            acl_secret = sub.get("acl_secret")
            expires = encoded_data.get("exp")
            # 将expires转换为datetime
            if expires:
                expires = datetime.fromtimestamp(expires)
                # 判断expires是否过期
                if expires < datetime.now():
                    raise unauthorized_exception
            if await acl_control_repo.is_acl_control_valid(db, acl_key, acl_secret, tenant_uuid):
                return response_base.success_simple(data={"tenant_uuid": tenant_uuid, "acl_key": acl_key, "acl_secret": acl_secret})
            else:
                raise unauthorized_exception
        else:
            raise unauthorized_exception
    except DecodeError as e:
        logger.warning(f"Token decode error: {str(e)}", exc_info=True)
        raise unauthorized_exception
    except ExpiredSignatureError:
        raise unauthorized_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}", exc_info=True)
        raise unauthorized_exception

TokenDeps = Depends(is_token_valid)