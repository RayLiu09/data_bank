from vectors.models.document import Document


class BaseRetrieval():
    """
    BaseRetrieval is a base class for retrieval.
    """
    def __init__(self):
        self.name = "BaseRetrieval"
        self.description = "A base retrieval class."

    def check_by_id(self, uuid: str) -> bool:
        """
        Check if the document exists by id.
        """
        return False

    def check_by_name(self, name: str) -> bool:
        """
        Check if the document exists by name.
        """
        return False

    def lists(self) -> list:
        """
        List all documents.
        """
        return []

    def get_document(self, uuid: str, includes: list = []) -> Document:
        """
        Get a document by id, and return with includes properties.
        """
        return None