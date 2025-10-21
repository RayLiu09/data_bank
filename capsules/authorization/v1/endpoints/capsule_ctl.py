import datetime
import json
import logging
import os.path
from http import HTTPStatus

from fastapi import APIRouter, UploadFile, Form, Body, Header

from capsules.authorization.models.claim import CapsuleClaimModel
from capsules.authorization.models.collector import CollectorPropModel
from capsules.authorization.services.capsule_srv import capsule_srv
from common.db_deps import SessionDep
from common.response_util import response_base
from security.token_deps import TokenDeps
from settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/collector", dependencies=[TokenDeps], summary="数据采集者将采集数据发送给数据拥有者")
async def collect(db: SessionDep, file: UploadFile, props: str = Form("{}", description="数据胶囊附加属性"), signature: str = Header(..., description="签名")):
    """
    Collect data capsule info, request data type: multipart/form-data, support upload file

    params:
    - file: uploaded file
    - props: Optional metadata info in JSON formatter
    """
    # 解析props参数
    try:
        # TODO: 验证发送者数字证书签名

        props_data = json.loads(props) if isinstance(props, str) else props
        print("props_data:", props_data)
        collector_props = CollectorPropModel(**props_data)
    except Exception as e:
        logger.error(f"Failed to parse props: {e}")
        collector_props = CollectorPropModel()
    
    # 将上传的数据文件保存到临时目录
    temp_dir = settings.tmp_dir
    # 确保临时目录存在
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    file_path = os.path.join(temp_dir, f"{file.filename}_{timestamp}")
    with open(file_path, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)

    logger.info(f"File saved successfully: {file_path}, size: {len(contents)} bytes, and content_type: {file.content_type}")
    try:
        response = await capsule_srv.wrap_data_capsule(db, file_path, collector_props)
        logger.info(f"Collect data capsule info successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"Collect data capsule info failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"Collect data capsule info failed: {str(e)}")

@router.get("/rawdata/{capsule_uuid}", dependencies=[TokenDeps], summary="获取数据胶囊原始数据")
async def get_raw_data(db: SessionDep, capsule_uuid: str):
    """
    Get raw data of data capsule

    params:
    - capsule_uuid: data capsule uuid
    """
    try:
        response = await capsule_srv.get_raw_data(db, capsule_uuid)
        logger.info(f"Get raw data of data capsule successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"Get raw data of data capsule failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"Get raw data of data capsule failed: {str(e)}")

@router.get("/list", dependencies=[TokenDeps], summary="获取数据胶囊列表")
async def list_capsules(db: SessionDep, offset: int = 0, limit: int = 10):
    """
    List data capsules

    params:
    - offset: page number
    - limit: page size
    """
    try:
        response = await capsule_srv.list_capsules(db, offset, limit)
        logger.info(f"List data capsules successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsules failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"List data capsules failed: {str(e)}")

@router.get("/{owner}/list", dependencies=[TokenDeps], summary="获取指定Owner的数据胶囊列表")
async def list_capsules_by_owner(db: SessionDep, owner: str, offset: int = 0, limit: int = 10):
    """
    List data capsules by owner

    params:
    - owner: owner of data capsule
    - offset: page number
    - limit: page size
    """
    try:
        response = await capsule_srv.list_capsules_by_owner(db, owner, offset, limit)
        logger.info(f"List data capsules by owner successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"List data capsules by owner failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"List data capsules by owner failed: {str(e)}")

@router.post("/grant", dependencies=[TokenDeps], summary="授权数据胶囊给其他用户")
async def grant_capsules(db: SessionDep, signature: str = Header(..., description="签名"), claim: CapsuleClaimModel = Body(..., description="授权信息")):
    """
    Grant data capsule to other users

    params:
    - claim: authorization info
    """
    try:
        response = await capsule_srv.grant_capsules(db, claim, signature)
        logger.info(f"Grant data capsule to other users successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"Grant data capsule to other users failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"Grant data capsule to other users failed: {str(e)}")

@router.get("/grant/access/{claim_uuid}", dependencies=[TokenDeps], summary="根据授权指令获取数据胶囊")
async def get_capsules_by_claim(db: SessionDep, claim_uuid: str, owner: str = Header(..., description="授权指令拥有者")):
    """
    Get data capsules by claim

    params:
    - claim_uuid: claim uuid
    """
    try:
        if not owner:
            return await response_base.fail(code=HTTPStatus.BAD_REQUEST, msg="Invalid owner")
        response = await capsule_srv.get_capsules_by_claim(db, claim_uuid, owner)
        logger.info(f"Get data capsule by claim successfully: {response}")
        return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=response)
    except Exception as e:
        logger.error(f"Get data capsule by claim failed: {e}")
        return await response_base.fail(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg=f"Get data capsule by claim failed: {str(e)}")
