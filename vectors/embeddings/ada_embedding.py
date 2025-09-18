import json
import logging
import os
import time

from weaviate.exceptions import WeaviateBatchValidationError, UnexpectedStatusCodeError
from weaviate.util import generate_uuid5

from settings import settings
from vectors.embeddings.base_embedding import BaseEmbedding
from vectors.engines.weaviate_engine import WeaviateEngine
from vectors.models.document import Document
from openai import OpenAI
from openai.resources import Embeddings

logger = logging.getLogger(__name__)


class AdaEmbedding(BaseEmbedding):
    """
    An embedding class for Ada embeddings.This embedding class is used for OpenAI' s models.
    """

    def __init__(self):
        super().__init__()
        self.name = "AdaEmbedding"
        self.batch_size = 100
        self.vectorizer = settings.default_openai_embedding_model
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        self.description = "Embedding and retrieves text data using OpenAI's Ada embeddings."

    def embed(self, doc: Document):
        self._exec_embed(doc)

    def _exec_embed(self, doc: Document):
        """
        Execute embedding for a single document
        """
        if self.vectorizer == "":
            logger.info(f"No vectorizer is provided for {self.name}.")

        client = WeaviateEngine().get_engine()
        try:
            start = time.time()
            logger.info(f"Embedding {doc.name} using {self.vectorizer}, and started at {start}")
            documents = client.collections.get("Documents")
            uuid = documents.data.insert(properties={
                        "content": doc.content,
                        "name": doc.name,
                        "ext": doc.ext,
                        "linker": "",
                        "metadata": json.dumps(doc.metadata),
                        "timestamp": doc.timestamp,
                        "chunk_count": len(doc.chunks),
                        # "embedding": self.openai_client.embeddings.create(
                        #     input=doc.content,
                        #     model=self.vectorizer
                        # ).data[0].embedding
                    })

            logger.info(f"Embedding {doc.name} completed, uuid {uuid} and executed time period {time.time() - start: .6f} seconds.")
            for chunk in doc.chunks:
                chunk.doc_uuid = uuid

            start = time.time()
            chunks = client.collections.get("Chunks")
            logger.info(f"Embedding chunks for {doc.name} using {self.vectorizer}, and started at {start}")
            with chunks.batch.dynamic() as batch:
                for chunk in doc.chunks:
                    embedding = Embeddings(self.openai_client).create(input=chunk.content, model=self.vectorizer)
                    if embedding.data[0].embedding is None:
                        logger.error(f"Generate embedding for {chunk.content} failed.")
                        continue

                    batch.add_object(
                        properties={
                            "content": chunk.content,
                            "chunk_id": chunk.chunk_id,
                            "doc_uuid": chunk.doc_uuid,
                            "doc_name": chunk.doc_name,
                            "metadata": json.dumps(chunk.metadata),
                            "timestamp": chunk.timestamp,
                            "tokens": chunk.tokens,
                        },
                        uuid=generate_uuid5(chunk),
                        vector=embedding.data[0].embedding)

                    rate_limit = os.getenv("EMBEDDING_RATE_LIMIT", 0)
                    if int(rate_limit) > 0:
                        logger.info(f"Sleep for {rate_limit} milliseconds.")
                        time.sleep(int(rate_limit) / 1000)
            logger.info(f"Embedding {doc.name} all chunks complete, and finished with {time.time() - start: .6f} seconds.")
            # Log all failed batch objects.
            logger.info(f"Failed batch objects: {json.dumps(client.batch.failed_objects, indent=2)}")
        except UnexpectedStatusCodeError as e:
            logger.error(f"Unexpected status code: {e}")
        except WeaviateBatchValidationError as e:
            logger.error(f"Batch error: {e}")
        finally:
            client.close()