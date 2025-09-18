import datetime
import logging
import os
from typing import Dict, List, Any

import weaviate.classes as wvc
from openai import OpenAI
from openai.resources import Embeddings
from weaviate.classes.query import MetadataQuery
from weaviate.exceptions import UnexpectedStatusCodeError, WeaviateConnectionError

from common.utils import convert_utc_to_local
from vectors.engines.weaviate_engine import WeaviateEngine

from vectors.retrievers.base_retriever import BaseRetrieval

logger = logging.getLogger(__name__)


class WeaviateRetriever(BaseRetrieval):
    """
    A retriever class for Weaviate.
    """

    def __init__(self):
        super().__init__()
        self.name = "WeaviateRetriever"
        self.description = "A retriever class for Weaviate."
        self.client = WeaviateEngine().get_engine()

    def check_by_id(self, uuid: str) -> bool:
        """
        Check if a document with the given UUID exists in the Weaviate database.
        """
        logger.info(f"Checking if document with UUID {uuid} exists in Weaviate database...")
        try:
            collection = self.client.collections.get("Documents")
            if collection is None:
                return False
            response = collection.query.fetch_object_by_id(uuid)
            if response is not None:
                logger.info(f"Document with UUID {uuid} exists in Weaviate database.")
                return True

            return False
        finally:
            self.client.close()

    def check_by_name(self, name: str) -> bool:
        logger.info(f"Checking if document with name {name} exists in Weaviate database...")
        try:
            collection = self.client.collections.get("Documents")
            if collection is None:
                return False

            response = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("name").equal(name)
            )

            if len(response.objects) > 0:
                logger.info(f"Document with name {name} exists in Weaviate database.")
                return True

            return False
        finally:
            self.client.close()

    async def list_all_docs(self, offset: int = 0, limit: int = 10) -> dict[str, list[dict[str, int | Any]] | Any]:
        """
        List all documents in the Weaviate database by pagination.

        Parameters:
            offset(int): Skip offset to start from.
            limit(int): Obtain the first limit documents.

        Returns:
            list[Document]: A list of documents.
        """
        logger.info("Listing all documents in Weaviate database...")
        try:
            collection = self.client.collections.get("Documents")
            if collection is None:
                return []
            total_response = collection.aggregate.over_all(total_count=True)
            logger.info(f"Found {total_response.total_count} documents in Weaviate database.")
            response = collection.query.fetch_objects(
                offset=offset,
                limit=limit,
                sort=wvc.query.Sort.by_property("timestamp", ascending=False)
            )
            docs = [{"uuid": doc.uuid, "name": doc.properties["name"],
                     "ext": doc.properties["ext"],
                     "timestamp": convert_utc_to_local(doc.properties["timestamp"]),
                     "linker": doc.properties["linker"],
                     "chunk_count": int(doc.properties["chunk_count"])} for doc in response.objects]
            logger.info(f"Found {len(docs)} documents in Weaviate database.")

            return {"total": total_response.total_count, "docs": docs}
        finally:
            self.client.close()

    async def list_all_chunks_by_doc_uuid(self, uuid: str, offset: int = 0, limit: int = 1000) -> list[dict]:
        """
        List all chunks of a document in the Weaviate database.

        Parameters:
            uuid(str): the uuid of the document.
            offset(int): Skip offset to start from.
            limit(int): Obtain the first limit chunks.

        Returns:
            list[dict]: A list of chunks.
        """
        logger.info(f"Listing all chunks of document with doc UUID {uuid} in Weaviate database...")
        try:
            collection = self.client.collections.get("Chunks")
            if collection is None:
                return []
            response = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("doc_uuid").equal(uuid),
                offset=offset,
                limit=limit,
                sort=wvc.query.Sort.by_property("chunk_id")
            )
            chunks = [{"uuid": doc.uuid, "content": doc.properties["content"],
                       "chunk_id": doc.properties["chunk_id"],
                       "doc_uuid": doc.properties["doc_uuid"],
                       "doc_name": doc.properties["doc_name"],
                       "timestamp": convert_utc_to_local(doc.properties["timestamp"])
                       } for doc in response.objects]
            logger.info(f"Found {len(chunks)} chunks of document with doc UUID {uuid} in Weaviate database.")
            return chunks
        finally:
            self.client.close()

    async def del_chunk_by_uuid(self, uuid: str) -> bool:
        """
        Delete a chunk by its UUID.

        Parameters:
            uuid(str): The UUID of the chunk.
        Returns:
            bool: Failure or Success
        """
        logger.info(f"Deleting chunk with UUID {uuid} in Weaviate database...")
        try:
            collection = self.client.collections.get("Chunks")
            if collection is None:
                return False

            response = collection.data.delete_by_id(uuid)
            if response:
                logger.info(f"Chunk with UUID {uuid} deleted in Weaviate database.")
                return True
            else:
                logger.error(f"Failed to delete chunk with UUID {uuid} in Weaviate database.")
                return False
        finally:
            self.client.close()

    async def del_document_by_uuid(self, uuid: str) -> bool:
        """
        Delete a document by its UUID.

        Parameters:
            uuid(str): The UUID of the document.
        Returns:
            bool: False or True
        """
        logger.info(f"Deleting document with UUID {uuid} in Weaviate database...")
        try:
            collection = self.client.collections.get("Documents")
            if collection is None:
                return False

            response = collection.data.delete_by_id(uuid)
            if response:
                logger.info(f"Document with UUID {uuid} deleted in Weaviate database.")
                await self.del_chunks_by_doc_uuid(uuid)
                return True
            else:
                logger.error(f"Failed to delete document with UUID {uuid} in Weaviate database.")
                return False
        finally:
            self.client.close()

    async def del_chunks_by_doc_uuid(self, uuid: str) -> bool:
        """
        Delete all chunks of a document by its UUID.

        Parameters:
            uuid(str): The UUID of the document.
        Returns:
            bool: False or True
        """
        logger.info(f"Deleting all chunks of document with UUID {uuid} in Weaviate database...")
        try:
            collection = self.client.collections.get("Chunks")
            if collection is None:
                return False

            response = collection.data.delete_many(
                where=wvc.query.Filter.by_property("doc_uuid").equal(uuid),
                verbose=False,
                dry_run=False
            )
            if response:
                logger.info(f"All chunks of document with UUID {uuid} deleted in Weaviate database.")
                return True
            else:
                logger.error(f"Failed to delete all chunks of document with UUID {uuid} in Weaviate database.")
                return False
        except WeaviateConnectionError as e:
            logger.error(f"Failed to delete all chunks of document with UUID {uuid} in Weaviate database: {e}")
            return False
        except UnexpectedStatusCodeError as e:
            logger.error(f"Failed to delete all chunks of document with UUID {uuid} in Weaviate database: {e}")
            return False
        finally:
            self.client.close()

    async def similarity_search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        A similarity search is a way to find similar documents to a given query.

        Parameters:
            query(str): the source text to search for.
            top_k(int): the most similar top k results to return.
        Returns:
            list[dict]: A list of documents.
        """
        logger.info(f"Performing similarity search for query '{query}' in Weaviate database...")
        try:
            collection = self.client.collections.get("Chunks")
            if collection is None:
                return []
            openai_client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE")
            )
            embedding = Embeddings(openai_client).create(input=query, model=constants.DEFAULT_OPENAI_EMBEDDING_MODEL)
            if embedding.data[0].embedding is None:
                logger.info(f"Failed to get embedding for query '{query}'.")
                return []

            response = collection.query.near_vector(
                near_vector=embedding.data[0].embedding,
                include_vector=True,
                limit=top_k,
                distance=constants.MAX_ACCEPTED_DISTANCE,
                return_metadata=MetadataQuery(distance=True)
            )

            chunks = [{"uuid": doc.uuid, "content": doc.properties["content"],
                       "chunk_id": doc.properties["chunk_id"],
                       "doc_uuid": doc.properties["doc_uuid"],
                       "doc_name": doc.properties["doc_name"],
                       "distance": doc.metadata.distance
                       } for doc in response.objects]
            logger.debug(f"Found similar chunks:--- \n{chunks}\n ---in Weaviate database.")
            return chunks
        finally:
            self.client.close()
