import json
import logging
from typing import Any

from openai import AsyncClient, APIConnectionError, RateLimitError

from llm.model_provider.model_base import ModelBase
from llm.prompts.bnf import get_capsule_section
from settings import settings

logger = logging.getLogger(__name__)


class CapsuleLoader:
    """
    Capsule的raw_data和summary_data准备类，主要用以与LLM交互获取对医疗影像报告数据的提取
    """
    def __init__(self, vendor: str):
        if vendor is None:
            vendor = settings.sel_model_provider
        self.model_base = ModelBase.instance(vendor)
        
        # 正确初始化AsyncClient，避免传递不支持的参数
        model_settings = self.model_base.model_settings
        client_kwargs = {
            "api_key": model_settings["api_key"]
        }
        
        # 只有在api_base存在且非空时才添加base_url参数
        if model_settings.get("api_base"):
            client_kwargs["base_url"] = model_settings["api_base"]
            
        # 确保不传递proxies等可能不支持的参数
        self.async_client = AsyncClient(**client_kwargs)

    async def calc_raw_data_by_bnf(self, origin_text: str) -> dict[str, Any] | None:
        """
        根据预定义的1阶胶囊的BNF表达式，由医疗检测报告原始数据中提取出BNF范式要求数据，并以JSON类型字符串输出

        Args:
            origin_text: str, 原始医疗数据报告内容
        Returns:
            符合BNF规范约束的JSON类型字符串
        """
        logger.info(f"Start to calc raw data using {self.model_base.model_settings['default_model']}")
        try:
            bnf_template = get_capsule_section("raw_data").format(text=origin_text)
            result = await self.async_client.chat.completions.create(
                model=self.model_base.model_settings["default_model"],
                messages=[
                    {"role": "system", "content": "You are a medical report extractor"},
                    {"role": "user", "content": bnf_template}
                ],
                temperature=self.model_base.temperature,
                top_p=self.model_base.top_p,
                stream=False
            )
            logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
            # 检查输出内容是否符合JSON格式
            json_data = json.loads(result.choices[0].message.content)
            logger.debug(f"The result of the query is: /n*******/n{json_data}/n*******")
            return json_data
        except APIConnectionError as e:
            logger.error(f"The server could not be reached: {e}")
        except RateLimitError as e:
            logger.error(f"A 429 status code was received; we should back off a bit. {e}")
        except Exception as e:
            logger.error(f"4xx or 5xx status code was received, its status is: {e.status_code}, "
                         f"and response {e.response}")
        finally:
            await self.async_client.close()

    async def calc_summary_data_by_bnf(self, origin_text: str) -> str | None:
        """
        根据输入的医疗检测报告原始数据，通过LLM提炼总结出不超过150字的概要信息

        Args:
            origin_text: str, 原始医疗数据报告内容
        Returns:
            医疗报告内容概要说明
        """
        logger.info(f"Start to calc summary data using {self.model_base.model_settings['default_model']}")
        bnf_template = get_capsule_section("summary_data").format(text=origin_text)
        try:
            result = await self.async_client.chat.completions.create(
                model=self.model_base.model_settings["default_model"],
                messages=[
                    {"role": "system", "content": "You are a medical report extractor"},
                    {"role": "user", "content": bnf_template}
                ],
                temperature=self.model_base.temperature,
                top_p=self.model_base.top_p,
                stream=False
            )
            logger.debug(f"The result of the query is: /n*******/n{result.choices[0].message.content}/n*******")
            return result.choices[0].message.content
        except APIConnectionError as e:
            logger.error(f"The server could not be reached: {e}")
        except RateLimitError as e:
            logger.error(f"A 429 status code was received; we should back off a bit. {e}")
        except Exception as e:
            logger.error(f"4xx or 5xx status code was received, its status is: {e.status_code}, "
                         f"and response {e.response}")
        finally:
            await self.async_client.close()

capsule_loader = CapsuleLoader(settings.sel_model_provider)