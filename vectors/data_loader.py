import logging
from pathlib import Path

from settings import settings
from vectors.chunkings.sentence_chunking import SentenceChunking
from vectors.chunkings.tiktoken_chunking import TiktokenChunking
from vectors.chunkings.word_chunking import WordChunking
from vectors.embeddings.ada_embedding import AdaEmbedding
from vectors.readers.common_reader import CommonReader
from vectors.readers.pdf_reader import PDFReader
from vectors.retrievers.weaviate_retriever import WeaviateRetriever

logger: logging.Logger = logging.getLogger(__name__)


class DataLoader:
    """
    DataLoader is a class that loads data from a file or directory and returns a list of documents.
    """
    def __init__(self):
        self.name = "DataLoader"
        self.description = "A data loader for loading data from a file or directory."
        self.extensions = [".txt", ".md", ".docx", ".pptx", ".pdf"]
        self.reader = None
        self.chunker = None
        self.embedder = None

    def load(self, file_name: str, file_dir: str = None, **kwargs):
        if file_name is not None:
            ext = Path(file_name).suffix.lower()
            if ext == '.pdf':
                self.reader = PDFReader()
            else:
                self.reader = CommonReader()

        if file_name is None and file_dir is not None:
            # Using PdfReader for PDF files within the directory
            logger.info("Here will only load PDF files within the directory")
            self.reader = PDFReader()

        documents = self.reader.load(file_name, file_dir, **kwargs)
        if not documents:
            logger.info("No documents found")

        for doc in documents:
            retriever = WeaviateRetriever()
            if retriever.check_by_name(doc.name):
                logger.info(f"Document {doc.name} already exists in the database")
                continue

            # Step into chunk documentation.
            chunk_type = settings.chunk_type
            if chunk_type == "sentence":
                self.chunker = SentenceChunking(unit=10, overlap=1)
            elif chunk_type == "word":
                self.chunker = WordChunking(unit=500, overlap=50)
            elif chunk_type == "token":
                self.chunker = TiktokenChunking(unit=512, overlap=50)
            else:
                raise ValueError(f"Invalid chunk way: {chunk_type}")

            chunk_doc = self.chunker.chunk_data(doc)
            logger.info(f"Chunked {len(chunk_doc.chunks)} chunks")

            # Step into embedding.
            self.embedder = AdaEmbedding()
            self.embedder.embed(chunk_doc)
            logger.info(f"Finish document {doc.name} vectorization.")
