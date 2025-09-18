from vectors.models.document import Document


class BaseChunking:
    def __init__(self):
        self.name = "BaseChunking"
        self.unit = 5
        self.overlap = 1
        self.description = "A base class for chunking data."

    def chunk_data(self, doc: Document) -> Document:
        raise NotImplementedError("Must provide a implementation in derived classes.")