import logging

from vectors.models.document import Document


logger = logging.getLogger(__name__)

class BaseEmbedding():
    def __init__(self):
        self.name = "BaseEmbedding"
        self.batch_size = 100
        self.vectorizer = ""

    def embed(self, doc: Document):
        """
        As OpenAI's API rate limit, there should have a back-off strategy to slow down requests when approaching the limit
        """
        raise NotImplementedError("Must provide a implementation in derived classes.")

    def _exec_embed(self, doc: Document):
        """
        Execute embedding for a single document
        """
        if self.vectorizer == "":
            logger.warn(f"No vectorizer is provided for {self.name}.")
