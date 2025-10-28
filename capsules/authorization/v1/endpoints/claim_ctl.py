#-*- coding:utf-8 -*-
import logging
from http import HTTPStatus

from fastapi import APIRouter

from capsules.authorization.services import claim_srv
from common.db_deps import SessionDep
from common.response_util import response_base
from security.token_deps import TokenDeps

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list", dependencies=[TokenDeps], summary="获取数据胶囊授权列表")
async def list_capsule_claims(db: SessionDep, offset: int = 0, limit: int = 10):
    """
    List data capsule claims
    """
    try:
        response = await claim_srv.list_claims(db, offset, limit)
        logger.info(f"List data capsule claims successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsule claims failed: {str(e)}")
        return await response_base.fail_simple(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=str(e))

@router.get("/list/by/owner/{owner}", dependencies=[TokenDeps], summary="根据授权发起者获取数据胶囊授权列表")
async def list_owner_capsule_claims(db: SessionDep, owner: str, offset: int = 0, limit: int = 10):
    """
    List data capsule claims
    """
    try:
        response = await claim_srv.get_claims_by_owner(db, owner, offset, limit)
        logger.info(f"List data capsule claims successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsule claims failed: {str(e)}")
        return await response_base.fail_simple(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=str(e))

@router.get("/list/by/receiver/{receiver}", dependencies=[TokenDeps], summary="根据授权接收者获取数据胶囊授权列表")
async def list_receiver_capsule_claims(db: SessionDep, receiver: str, offset: int = 0, limit: int = 10):
    """
    List data capsule claims
    """
    try:
        response = await claim_srv.get_claims_by_receiver(db, receiver, offset, limit)
        logger.info(f"List data capsule claims successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsule claims failed: {str(e)}")
        return await response_base.fail_simple(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=str(e))
