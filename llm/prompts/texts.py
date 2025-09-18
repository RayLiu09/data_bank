from typing import Annotated

from fastapi import Depends

from llm.model_provider.options import TargetPlatform

_all_templates = {
    "little_red_book": {
        "title": "请生成{number}条以{subject}为主题的符合小红书风格的爆款标题，要求包含文字和emoji表情",
        "content": """
        小红书的风格是：很吸引眼球的标题，每个段落都加 emoji, 最后加一些 tag。请用小红书风格生成一篇以{subject}为主题的文案，要求输出文字风格为{style}, 字数不小于{number}。
        """,
    },
    "community": {
        "title": "请生成{number}条以{subject}为主题的符合社群风格的爆款标题",
        "content": """
        请生成一篇符合社群软文风格的以{subject}为主题的文案，要求输出文字风格为{style}, 字数不小于{number}, 。
        """,
    },
    "wechat": {
        "title": "请生成{number}条以{subject}为主题的符合微信公众号风格的爆款标题",
        "content": """
        请生成一篇符合微信公众号风格的以{subject}为主题的文案，要求输出文字风格为{style}, 字数不小于{number}
        """,
    },
    "weibo": {
        "title": "请生成{number}条以{subject}为主题的符合微博风格的爆款标题",
        "content": """
        请生成一篇符合微博风格的以{subject}为主题的文案，要求输出文字风格为{style}, 字数不小于{number}。
        """,
    },
    "tiktok": {
        "title": "请生成{number}条以{subject}为主题的符合抖音短视频标题的爆款标题",
        "content": """
        请生成一篇符合抖音短视频标题的以{subject}为主题的短视频脚本，要求输出文字风格为{style}, 视频时长不小于{number}秒。
        """,
    }
}

async def get_template(target_platform: TargetPlatform) -> dict[str, str]:
    return _all_templates[target_platform.name]

TemplateDeps = Annotated[dict[str, str], Depends(get_template)]