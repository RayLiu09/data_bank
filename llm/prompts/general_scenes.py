from typing import Annotated

from fastapi import Depends

_all_scenes = {
    'summarize': """
    {CONTEXT}
    
    请基于上述内容总结摘要出提供内容的核心思想，要求{QUERY}，不要随意扩写、延伸内容范围。
    """,
    'translate': """
    {CONTEXT}
    
    下面我让你来充当翻译家，你的目标是把任何语言翻译成用户指定的语言，请翻译时不要带翻译腔，而是要翻译得自然、流畅和地道，使用优美和高雅的表达方式。请根据用户要求{QUERY}翻译上述内容。
    """,
    'modification': """
    {CONTEXT}
    
    请根据用户要求{QUERY}将上述文案进行润色优化，并进行改写使其修辞更加优雅。
    """,
    'extend': """
    {CONTEXT}
    
    请根据用户要求{QUERY}，将上述文案进行扩写以充实、丰富内容，不要随意修改原文的主要思想。
    """,
    'completion': """
    {CONTEXT}
    
    请根据用户要求{QUERY}，继续完成上述文案内容，不要修改已给出文案部分内容。
    """
}
async def get_scene(scene_name: str) -> str:
    return _all_scenes[scene_name]

SceneDeps = Annotated[str, Depends(get_scene)]
