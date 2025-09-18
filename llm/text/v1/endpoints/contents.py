import logging

from fastapi import APIRouter, Query, HTTPException, File, Form, UploadFile

from llm.model_provider.options import Vendor, TargetPlatform, StyleName, EcommerceType
from llm.prompts.e_commerce import get_type
from llm.prompts.role_settings import get_title_role, get_content_role
from llm.prompts.texts import get_template
from llm.text.exec_handler import do_title, do_content, do_action_proc, convert_style_proc, create_ecommerce_proc
from llm.text.models import TitlePayload, ContentPayload, ContextActionPayload, EcommercePayload
from security.token_deps import TokenDeps

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/title", dependencies=[TokenDeps], summary="创建指定平台的爆款标题")
async def create_title(payload: TitlePayload,
                       target_platform: TargetPlatform = Query(default=TargetPlatform.little_red_book, description="目标平台"),
                       vendor: Vendor = Query(default=Vendor.openai, description="模型供应商")):
    if not payload:
        raise HTTPException(status_code=400, detail="用户参数为空")

    return await do_title(payload, vendor, await get_title_role(target_platform), await get_template(target_platform))


@router.post("/text", dependencies=[TokenDeps], summary="创建指定平台的爆款内容")
async def create_content(payload: ContentPayload,
                        target_platform: TargetPlatform = Query(default=TargetPlatform.little_red_book, description="目标平台"),
                        vendor: Vendor = Query(default=Vendor.openai, description="模型供应商")):
    if not payload:
        raise HTTPException(status_code=400, detail="用户参数为空")
    return await do_content(payload, vendor, await get_content_role(target_platform), await get_template(target_platform))

@router.post("/action", dependencies=[TokenDeps], summary="对指定内容进行改写、扩写、续写或简写")
async def do_action(payload: ContextActionPayload,
                    vendor: Vendor = Query(default=Vendor.openai, description="模型供应商")):
    if not payload:
        raise HTTPException(status_code=400, detail="用户参数为空")
    return await do_action_proc(payload, vendor)

@router.post("/convert", dependencies=[TokenDeps], summary="将文本转换为指定风格")
async def convert_style(text: str = Form(default="", description="文本内容"), file: UploadFile = File(default=None, description="文本文件"),
                        style_name: StyleName = Query(default=StyleName.little_red_book, description="目标风格"),
                        vendor: Vendor = Query(default=Vendor.openai, description="模型供应商")):
    if not text and not file:
        raise HTTPException(status_code=400, detail="用户参数为空")
    if not text and file:
        text = file.file.read().decode("utf-8")
    return await convert_style_proc(text, vendor, style_name)

@router.post("/ecommerce", dependencies=[TokenDeps], summary="生成电商产品文案")
async def create_ecommerce(payload: EcommercePayload,
                           prod_type: EcommerceType = Query(default=EcommerceType.prod_marketing, description="产品类型"),
                           vendor: Vendor = Query(default=Vendor.openai, description="模型供应商")):
    if not payload:
        raise HTTPException(status_code=400, detail="用户参数为空")

    return await create_ecommerce_proc(payload, await get_type(prod_type.name), vendor)