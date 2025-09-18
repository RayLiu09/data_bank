import logging

import weaviate.classes as wvc
import weaviate.classes.config as wvcc
from weaviate.exceptions import WeaviateConnectionError, UnexpectedStatusCodeException

from vectors.engines.weaviate_engine import WeaviateEngine

logger: logging.Logger = logging.getLogger(__name__)


class SchemaInitializer:
    """
    An initializer class for creating and managing vector schema.
    """

    @staticmethod
    def create_schema():
        client = WeaviateEngine().get_engine()
        try:
            # Setup document collection.
            if not client.collections.exists("Documents"):
                collection = client.collections.create(
                    name="Documents",
                    description="The documents collection contains all the books and courses knowledge.",
                    vectorizer_config=None,
                    # vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY")),
                    # generative_config=wvcc.Configure.Generative.openai(model="gpt-4"),
                    vector_index_config=wvcc.Configure.VectorIndex.hnsw(distance_metric=wvc.config.VectorDistances.COSINE),
                    replication_config=wvcc.Configure.replication(factor=1),
                    multi_tenancy_config=wvcc.Configure.multi_tenancy(enabled=False),
                    properties=[
                        wvcc.Property(
                            name="content",
                            data_type=wvcc.DataType.TEXT,
                            description="Content of the document",
                            vectorize_property_name=False,
                            skip_vectorization=True,
                            index_filterable=False,
                            index_searchable=False,
                            tokenization=wvcc.Tokenization.GSE # Used for Chinese and Japanese.
                        ),
                        wvcc.Property(
                            name="name",
                            data_type=wvcc.DataType.TEXT,
                            description="Document name",
                            vectorize_property_name=False,
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="ext",
                            data_type=wvcc.DataType.TEXT,
                            description="Document type",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="linker",
                            data_type=wvcc.DataType.TEXT,
                            description="Linker for the document",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="timestamp",
                            data_type=wvcc.DataType.TEXT,
                            description="Timestamp of the document",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="metadata",
                            data_type=wvcc.DataType.TEXT,
                            description="Metadata of the document",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="chunks_count",
                            data_type=wvcc.DataType.NUMBER,
                            description="Number of chunks in the document",
                            skip_vectorization=True
                        ),
                    ]
                )
                logger.info(f"Schema created: {collection.config}")

            # Setup chunks collection.
            if not client.collections.exists("Chunks"):
                collection = client.collections.create(
                    name="Chunks",
                    description="The chunks collection contains all the chunks of the specified document.",
                    vectorizer_config=None,
                    # vectorizer_config=wvcc.Configure.Vectorizer.text2vec_openai(base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY")),
                    # generative_config=wvcc.Configure.Generative.openai(model="gpt-4"),
                    vector_index_config=wvcc.Configure.VectorIndex.hnsw(distance_metric=wvc.config.VectorDistances.COSINE),
                    replication_config=wvcc.Configure.replication(factor=1),
                    multi_tenancy_config=wvcc.Configure.multi_tenancy(enabled=False),
                    properties=[
                        wvcc.Property(
                            name="content",
                            data_type=wvcc.DataType.TEXT,
                            description="Content of the chunk",
                            vectorize_property_name=False,
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="chunk_id",
                            data_type=wvcc.DataType.NUMBER,
                            description="ID of the chunk",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="doc_uuid",
                            data_type=wvcc.DataType.TEXT,
                            description="UUID of the document",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="tokens",
                            data_type=wvcc.DataType.NUMBER,
                            description="Number of tokens in the chunk",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="metadata",
                            data_type=wvcc.DataType.TEXT,
                            description="Metadata of the chunk",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="timestamp",
                            data_type=wvcc.DataType.TEXT,
                            description="Timestamp of the chunk",
                            skip_vectorization=True
                        ),
                        wvcc.Property(
                            name="doc_name",
                            data_type=wvcc.DataType.TEXT,
                            description="Name of the document",
                            skip_vectorization=True
                        )
                    ],
                    # If here needs inverted index?
                    # inverted_index_config=wvcc.Configure.inverted_index(
                    #     bm25_b=0.75,
                    #     bm25_k1=1.25,
                    #     index_null_state=True, # perform queries that filter on null
                    #     index_property_length=True, # perform queries that filter on the length of a property
                    #     index_timestamps=True, # timestamps include creationTimeUnix and lastUpdateTimeUnix, execute queries filtered by timestamps
                    #     stopwords_preset=StopwordsPreset.NONE,
                    #     stopwords_additions=[],
                    #     stopwords_removals=[]
                    # )
                )
                logger.info(f"Schema created: {collection.config}")
        except WeaviateConnectionError as e:
            logger.error(f"Weaviate connection error: {e}")
        except UnexpectedStatusCodeException as e:
            logger.error(f"Unexpected status code exception: {e}")
        finally:
            client.close()