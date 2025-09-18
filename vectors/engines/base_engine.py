from typing import Generator, Any


class BaseEngine():
    """
    This is a blank vector store engine
    """

    def __init__(self):
        self.name = "EmptyEngine"
        self.description = "A blank vector store engine."

    def get_engine(self) -> Generator[Any, None, None]:
        raise NotImplementedError("The vector engine was not implemented")