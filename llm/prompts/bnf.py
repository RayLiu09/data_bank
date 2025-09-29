from typing import Annotated

from fastapi.params import Depends

_capsule_section = {
    "raw_data": """
    我为健康检查报告设计了一个BNF范式的结构描述如下： 

    <健康检查报告> ::= <生成时间戳><生成单位><报告单内容>； <生成时间戳> ::= <可确认加密>(<时间>)； <健康检查报告> ::= <生成时间戳><生成单位><报告单内容> <报告单内容> ::= <血液检查>｜<B超检查>｜<CT检查> <血液检查> :: = {<血液指标>}+ <血液指标> ::= <指标名><指标值><范围下限><范围上限> <B超检查> ｜<CT检查> :: = {<器官情况>}+ <器官情况> ::= <器官名><测量值><状态评价> 
    
    -----分割线------下面的是报告单内容，请识别并分解为BNF范式的结构，然后生成一个json格式的内容输出，请不要输出```json。
    ------------分割线---------------
    {text}
    """,
    "summary_data": """
    -----分割线------下面的是报告单内容，请认真阅读理解报告内容，并输出一段50字左右的检查报告简要概述。
    ------------分割线---------------
    {text}
    """,
}

def get_capsule_section(section_name: str) -> str:
    return _capsule_section[section_name]

SectionDep = Annotated[str, Depends(get_capsule_section)]