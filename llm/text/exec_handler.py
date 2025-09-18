import logging

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from openai import AsyncClient, APIConnectionError, RateLimitError, APIStatusError

from llm.model_provider.model_base import ModelBase
from llm.model_provider.options import Vendor, StyleName, TargetPlatform
from llm.prompts.general_scenes import get_scene
from llm.prompts.general_styles import get_style
from llm.prompts.role_settings import get_content_role
from llm.text.models import TitlePayload, ContentPayload, ContextActionPayload, EcommercePayload

logger = logging.getLogger(__name__)

async def do_title(payload: TitlePayload, vendor: Vendor, template: str, prompt: dict[str, str]):
    """
    创建指定发布平台的软文标题
    :param prompt: 提示词模版
    :param payload: 用户指定参数对象
    :param vendor: 选择的LLM模型厂商
    :param template: 用于设置System Prompt的模版
    :return:
    """
    base_model = ModelBase.instance(vendor.name)
    print(f"******{jsonable_encoder(base_model)}*****")
    client = AsyncClient(api_key=base_model.model_settings["api_key"], base_url=base_model.model_settings["api_base"])
    logger.info(f"Start to create titles using {vendor.value}")
    try:
        logger.debug(f"Using the template/n{template}/nto generate the results")
        query = prompt["title"].format(subject=payload.subject, number=[payload.number if payload.number else 10])
        result = await client.chat.completions.create(
            model=base_model.model_settings["default_model"],
            messages=[
                {"role": "system", "content": template},
                {"role": "user", "content": query}
            ],
            temperature=base_model.temperature,
            top_p=base_model.top_p,
            stream=False
        )
        logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
        return result.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"The server could not be reached: {e}")
    except RateLimitError as e:
        logger.error("A 429 status code was received; we should back off a bit.")
    except APIStatusError as e:
        logger.error(f"4xx or 5xx status code was received, its status is: {e.status_code}, "
                     f"and response {e.response}")
    finally:
        await client.close()

async def do_content(payload: ContentPayload, vendor: Vendor, template: str, prompt: dict[str, str]):
    """
    创建指定发布平台的软文正文
    :param payload: 用户指定参数对象
    :param vendor: 选择的LLM模型厂商
    :param template: 用于设置System Prompt的模版
    :return:
    """
    base_model = ModelBase.instance(vendor.name)
    client = AsyncClient(api_key=base_model.model_settings["api_key"], base_url=base_model.model_settings["api_base"])
    logger.info(f"Start to create contents using {vendor.value}")
    try:
        logger.debug(f"Using the template/n{template}/nto generate the results")
        query = prompt["content"].format(subject=payload.subject, number=payload.number, style=payload.style)
        result = await client.chat.completions.create(
            model=base_model.model_settings["default_model"],
            messages=[
                {"role": "system", "content": template},
                {"role": "user", "content": query}
            ],
            temperature=base_model.temperature,
            top_p=base_model.top_p,
            stream=False
        )
        logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
        return result.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"The server could not be reached: {e}")
    except RateLimitError as e:
        logger.error(f"A 429 status code was received; we should back off a bit. {e}")
    except APIStatusError as e:
        logger.error(f"4xx or 5xx status code was received, its status is: {e.status_code}, "
                     f"and response {e.response}")
    finally:
        await client.close()

async def do_action_proc(payload: ContextActionPayload, vendor: Vendor):
    """
    执行指定动作的文案处理任务
    :param payload: 用户指定参数对象
    :param vendor: 选择的LLM模型厂商
    :param template: 用于设置System Prompt的模版
    :return:
    """
    base_model = ModelBase.instance(vendor.name)
    client = AsyncClient(api_key=base_model.model_settings["api_key"], base_url=base_model.model_settings["api_base"])
    logger.info(f"Start to do action using {vendor.value}")
    try:
        logger.debug(f"Do the action {payload.action.value}")
        template = await get_scene(payload.action.name)
        query = template.format(CONTEXT=payload.context, QUERY=payload.prompt)
        result = await client.chat.completions.create(
            model=base_model.model_settings["default_model"],
            messages=[
                {"role": "user", "content": query}
            ],
            temperature=base_model.temperature,
            top_p=base_model.top_p,
            stream=False
        )
        logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
        return result.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"The server could not be reached: {e}")
    except RateLimitError as e:
        logger.error(f"A 429 status code was received; we should back off a bit. {e}")
    except APIStatusError as e:
        logger.error(
            f"4xx or 5xx status code was received, its status is: {e.status_code}, "
            f"and response {e.response}"
        )
    finally:
        await client.close()

async def convert_style_proc(text: str, vendor: Vendor, style_name: StyleName):
    """
    将文本转换为指定风格
    :param vendor:
    :param style_name:
    :param text: 文本内容
    :return:
    """
    base_model = ModelBase.instance(vendor.name)
    client = AsyncClient(api_key=base_model.model_settings["api_key"], base_url=base_model.model_settings["api_base"])
    logger.info(f"Start to convert style using {vendor.value}")
    try:
        logger.debug(f"Convert original text to style for {style_name}")
        template = await get_content_role(TargetPlatform.to_enum(style_name.name))
        style = await get_style(style_name)
        query = style.format(text=text)
        result = await client.chat.completions.create(
            model=base_model.model_settings["default_model"],
            messages=[
                {
                    "role": "system", "content": template
                },
                {
                    "role": "user", "content": query
                }
            ],
            temperature=base_model.temperature,
            top_p=base_model.top_p,
            stream=False
        )
        logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
        return result.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"The server could not be reached: {e}")
    except RateLimitError as e:
        logger.error(f"A 429 status code was received; we should back off a bit. {e}")
    except APIStatusError as e:
        logger.error(
            f"4xx or 5xx status code was received, its status is: {e.status_code}, "
            f"and response {e.response}"
        )
    finally:
        await client.close()

async def create_ecommerce_proc(payload: EcommercePayload, template: dict, vendor: Vendor):
    """
    生成电商产品文案
    :param payload:
    :param template:
    :param vendor:
    :return:
    """
    base_model = ModelBase.instance(vendor.name)
    client = AsyncClient(api_key=base_model.model_settings["api_key"], base_url=base_model.model_settings["api_base"])
    logger.info(f"Start to create ecommerce content using {vendor.value}")
    query = template["user_prompt"].format(background=payload.background, number=payload.number, subject=payload.subject)
    try:
        result = await client.chat.completions.create(
            model=base_model.model_settings["default_model"],
            messages=[
                {"role": "system", "content": template["sys_prompt"]},
                {"role": "user", "content": query}
            ],
            temperature=base_model.temperature,
            top_p=base_model.top_p,
            stream=False
        )
        logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
        return result.choices[0].message.content
    except APIConnectionError as e:
        logger.error(f"The server could not be reached: {e}")
    except RateLimitError as e:
        logger.error(f"A 429 status code was received; we should back off a bit. {e}")
    except APIStatusError as e:
        logger.error(
            f"4xx or 5xx status code was received, its status is: {e.status_code}, "
            f"and response {e.response}"
        )
    finally:
        await client.close()