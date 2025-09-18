from enum import Enum


class Vendor(str, Enum):
    openai = "OpenAI"
    qwen = "通义千问"
    vol = "字节豆包"

class TuneDirection(str, Enum):
    """
    文案微调方向
    """
    summarize = "摘要"
    translate = "翻译"
    extend = "扩写"
    modification = "改写"
    completion = "续写"

class TargetPlatform(str, Enum):
    """
    文案面向目标平台
    """
    weibo = "微博"
    wechat = "微信公众号"
    little_red_book = "小红书"
    community = "社群"
    tiktok = "抖音"

    @classmethod
    def to_enum(cls, target_platform: str):
        for platform in TargetPlatform:
            if platform.name == target_platform:
                return platform
        raise ValueError(f"Invalid target platform: {target_platform}")

class StyleName(str, Enum):
    """
    文案风格
    """
    little_red_book = "小红书"
    weibo = "微博"
    wechat = "微信公众号"
    community = "社群"
    warm_and_truth = "微暖真诚",
    humorous = "幽默风趣",
    sophisticated = "专业精妙",
    normal = "标准formal",
    science = "科学严谨"

    @classmethod
    def to_enum(cls, style_name: str):
        for style in StyleName:
            if style.name == style_name:
                return style
        raise ValueError(f"Invalid style name: {style_name}")

class EcommerceType(str, Enum):
    """
    电商类型
    """
    prod_marketing = "产品营销文案"
    prod_title = "产品标题"

    @classmethod
    def to_enum(cls, prod_type: str):
        for prod in EcommerceType:
            if prod.name == prod_type:
                return prod
        raise ValueError(f"Invalid product type: {prod_type}")