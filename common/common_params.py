from typing import Annotated

from fastapi import Query, Depends


async def paged_params(page: int = Query(1, description='页码', gt=0), page_size: int = Query(100, description='每页数量', gt=0)):
    """分页参数校验"""
    return {'offset': page, 'limit': page_size}

page_params = Annotated[dict, Depends(paged_params)]