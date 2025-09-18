import logging
import os
import weaviate

from settings import settings
from vectors.engines.base_engine import BaseEngine

logger: logging.Logger = logging.getLogger(__name__)


class WeaviateEngine(BaseEngine):
    """
    A vector store engine for Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "WeaviateEngine"
        self.description = "A vector store engine for Weaviate."
        self.host = settings.weaviate_host
        self.http_port = settings.weaviate_port
        self.grpc_port = settings.weaviate_grpc_port

    def get_engine(self) -> weaviate.WeaviateClient:
        logger.info(f"Connecting to Weaviate at {self.host}:{self.http_port} with headers: {os.getenv('OPENAI_BASE_URL')}")
        return weaviate.connect_to_custom(
            http_host=self.host,
            http_port=int(self.http_port),
            http_secure=False,
            grpc_host=self.host,
            grpc_port=int(self.grpc_port),
            grpc_secure=False,
            # headers={
            #     "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY"),
            #     "X-OpenAI-BaseUrl": os.getenv("OPENAI_API_BASE")
            # },
            skip_init_checks=True
        )
        # return weaviate.connect_to_local(host=self.host, port=int(self.http_port), grpc_port=int(self.grpc_port), skip_init_checks=True)
