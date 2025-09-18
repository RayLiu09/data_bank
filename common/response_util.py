#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Optional, Union, Set, Dict

from asgiref.sync import sync_to_async
from fastapi.encoders import jsonable_encoder
from pydantic import validate_call

_ExcludeData = Union[Set[Union[int, str]], Dict[Union[int, str], Any]]

__all__ = ['response_base']


class ResponseBase:
    """
    统一返回方法

    .. tip::

        此类中的返回方法将通过自定义编码器预解析，然后由 fastapi 内部的编码器再次处理并返回，可能存在性能损耗，取决于个人喜好

    E.g. ::

        @router.get('/test')
        def test():
            return await response_base.success(data={'test': 'test'})
    """  # noqa: E501

    @staticmethod
    @sync_to_async
    def __json_encoder(data: Any, exclude: Optional[_ExcludeData] = None, **kwargs):
        # custom_encoder = {datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)}
        # kwargs.update({'custom_encoder': custom_encoder})
        result = jsonable_encoder(data, exclude=exclude, **kwargs)
        return result

    @validate_call
    async def success(
            self,
            *,
            code: int = 200,
            msg: str = 'Success',
            data: Optional[Any] = None,
            exclude: Optional[_ExcludeData] = None,
            total: int = 0,
            page: int = 1,
            page_size: int = 20,
            **kwargs,
    ) -> dict:
        """
        请求成功返回通用方法

        :param page_size:
        :param page:
        :param total:
        :param code: 返回状态码
        :param msg: 返回信息
        :param data: 返回数据
        :param exclude: 排除返回数据(data)字段
        :return:
        """
        data = data if data is None else await self.__json_encoder(data, exclude, **kwargs)
        return {'code': code, 'message': msg, 'data': data,  "total": total, "page": page, "page_size": page_size}

    @validate_call
    async def success_simple(
            self,
            *,
            code: int = 200,
            msg: str = 'Success',
            data: Optional[Any] = None,
            exclude: Optional[_ExcludeData] = None,
            **kwargs,
    ) -> dict:
        """
        简化的请求成功返回通用方法，不包含分页信息

        :param code: 返回状态码
        :param msg: 返回信息
        :param data: 返回数据
        :param exclude: 排除返回数据(data)字段
        :return: 不包含分页信息的响应字典
        """
        data = data if data is None else await self.__json_encoder(data, exclude, **kwargs)
        return {'code': code, 'message': msg, 'data': data}

    @validate_call
    async def fail(
            self,
            *,
            code: int = 400,
            msg: str = 'Bad Request',
            data: Any = None,
            exclude: Optional[_ExcludeData] = None,
            **kwargs,
    ) -> dict:
        data = data if data is None else await self.__json_encoder(data, exclude, **kwargs)
        return {'code': code, 'message': msg, 'data': data}


response_base = ResponseBase()

class AuthException(Exception):
    """
    自定义令牌异常AuthException
    """
    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class PermissionException(Exception):
    """
    自定义权限异常PermissionException
    """
    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class LoginException(Exception):
    """
    自定义登录异常LoginException
    """
    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message

