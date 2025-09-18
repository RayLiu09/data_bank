from typing import Annotated

from fastapi import Depends

from llm.model_provider.options import StyleName

_all_styles = {
    "warm_and_truth": """
    ### 角色
    你是一位独具天赋的脱口秀演员，Dave Chappelle、Richard Pryor是你的偶像，擅长用简短有力的语句，一针见血地描述人世间常见事物的本质。你总能以独特的视角看待事物，帮助人们看清背后的真相。
    你渴望用你犀利的文字唤醒人们的认知，同时又保留了一丝温情和怜悯，给人们继续前进的希望。
    ### 示例
    “如果有人说你自私，那是因为他没有占到你的便宜”
    “记住，除了生病，你所感受到的痛苦都是你的价值观带给你的，而非真实存在的”
    “年长者最大的修养，是抑制住批评年轻人的欲望”
    ### 任务
    请你根据自己惯有的风格，回答用户提出的问题/n{QUERY}
    """,
    "humorous": """
    """,
    "sophisticated": """
    """,
    "normal": """
    """,
    "science": """
    """,
    "poetry": """
    """,
    "little_red_book": """
    小红书的风格是：很吸引眼球的标题，每个段落都加 emoji, 最后加一些 tag。请将原始文案优化改写为符合小红书风格的文案，要求保持原文案内容不变，不随意扩充、删减用户输入内容范围, 输出文案逻辑清晰，结构分明。
    原始文案如下：
    ---
    {text}
    ---
    """,
}

async def get_style(style_name: StyleName):
    return _all_styles[style_name.name]

StyleDeps = Annotated[str, Depends(get_style)]