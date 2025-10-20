# -*- coding: utf-8 -*-
import logging

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)
logger.info("Starting devices router")

@router.get("/", summary="获取活跃设备列表")
async def get_devices():
    """
    获取活跃设备列表
    """
    return {"message": "Hello World"}