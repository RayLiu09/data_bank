import datetime
import logging
import os.path
from http import HTTPStatus

from fastapi import APIRouter, UploadFile, Body, Form
from multipart.multipart import File

from capsules.authorization.models.collector import CollectorPropModel
from common.db_deps import SessionDep
from common.response_util import response_base
from security.token_deps import TokenDeps
from settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

router.post("/collector", dependencies=[TokenDeps], summary="数据采集者将采集数据发送给数据拥有者")
async def collect(db: SessionDep, file: UploadFile = File(...), props: CollectorPropModel = Form(..., description="数据胶囊附加属性")):
    """
    Collect data capsule info, request data type: multipart/form-data, support upload file

    params:
    - file: uploaded file
    - props: Optional metadata info in JSON formatter
    """
    # 将上传的数据文件保存到临时目录
    temp_dir = settings.tmp_dir
    file_path = os.path.join(temp_dir, file.filename + "_" + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S%f'))
    with open(file_path, 'wb') as buffer:
        contents = await file.read()
        buffer.write(contents)

    logger.info(f"File saved successfully: {file_path}, size: {len(contents)} bytes, and content_type: {file.content_type}")
    return response_base.success_simple(code=HTTPStatus.OK, msg='Success')