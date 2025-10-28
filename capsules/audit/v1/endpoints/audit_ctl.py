#-* -*- coding:utf-8 -*-
import logging
from http import HTTPStatus

from fastapi import APIRouter

from capsules.audit.services.audit_srv import audit_srv
from common.db_deps import SessionDep
from common.response_util import response_base
from security.token_deps import TokenDeps

logger = logging.getLogger(__name__)

router = APIRouter()
@router.get("/list", dependencies=[TokenDeps], summary="获取数据胶囊审计日志")
async def list_capsule_audits(db: SessionDep, offset: int = 0, limit: int = 10):
    """
    List data capsule audits
    """
    try:
        response = await audit_srv.list_audits(db, offset, limit)
        logger.info(f"List data capsule audits successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsule audits failed: {str(e)}")
        return await response_base.fail_simple(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=str(e))
