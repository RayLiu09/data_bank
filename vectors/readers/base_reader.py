from ..models.document import Document


class BaseReader():
    def __init__(self):
        self.name = "BaseReader"
        self.description = "A base reader"
        self.extensions = []

    def load(self, file_name: str, file_dir: str, contents: list[str], **kwargs) -> list[Document]:
        raise NotImplementedError("Must provide a implementation in derived classes")
