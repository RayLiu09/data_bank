from typing import Any


class BusException(Exception):
    """
    业务异常，用于抛出异常，并返回错误信息给前端
    """

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data