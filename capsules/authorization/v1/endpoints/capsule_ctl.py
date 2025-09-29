import datetime
import logging
import os.path
from http import HTTPStatus

from fastapi import APIRouter, UploadFile, Form
from typing import Optional
import json

from capsules.authorization.models.collector import CollectorPropModel
from capsules.authorization.services.capsule_srv import capsule_srv
from common.db_deps import SessionDep
from common.response_util import response_base
from security.token_deps import TokenDeps
from settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/collector", dependencies=[TokenDeps], summary="数据采集者将采集数据发送给数据拥有者")
async def collect(db: SessionDep, file: UploadFile, props: str = Form("{}", description="数据胶囊附加属性")):
    """
    Collect data capsule info, request data type: multipart/form-data, support upload file

    params:
    - file: uploaded file
    - props: Optional metadata info in JSON formatter
    """
    # 解析props参数
    try:
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