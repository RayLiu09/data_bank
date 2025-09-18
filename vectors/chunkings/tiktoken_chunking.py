# encoding=utf-8
"""
This module provides a class for chunking text into tokens.
"""

import logging

import tiktoken

from vectors.chunkings.base_chunking import BaseChunking
from vectors.models.chunk import Chunk
from vectors.models.document import Document

logger = logging.getLogger(__name__)


class TiktokenChunking(BaseChunking):
    """
    A chunking class for splitting text into tokens.
    """

    def __init__(self, unit: int, overlap: int, **kwargs):
        super().__init__()
        self.name = "TokenChunking"
        self.unit = unit | 512 # 256 或 512对于text-embedding-ada-002模型表现更好
        self.overlap = overlap | 50 #50
        self.description = "A chunking class for splitting text into tokens."
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def chunk_data(self, doc: Document) -> Document:
        """
        Chunk the data into tokens.
        And based-up on the unit and overlap, each chunk includes number of unit tokens.
        There is overlap between each chunk.
        """
        if len(doc.chunks) > 0:
            logger.info("Chunks already exist. Skipping chunking.")
            return doc

        encoded_tokens = self.encoding.encode(doc.content, disallowed_special=())
        if self.unit > len(encoded_tokens):
            logger.info("Unit is greater than the doc content. Skipping chunking.")
            chunk = Chunk(
                doc_name=doc.name,
                content=doc.content,
                chunk_id=0
            )
            doc.chunks.append(chunk)
            return doc

        i = 0
        spliter_id = 0
        while i < len(encoded_tokens):
            start_i = i
            end_i = i + self.unit
            if end_i > len(encoded_tokens):
                end_i = len(encoded_tokens)

            chunk_tokens = encoded_tokens[start_i:end_i]
            chunk_text = self.encoding.decode(chunk_tokens)

            doc_chunk = Chunk(
                doc_name=doc.name,
                content=chunk_text,
                chunk_id=spliter_id
            )
            doc.chunks.append(doc_chunk)
            spliter_id += 1

            # Exit loop if this is the last chunk
            if end_i == len(encoded_tokens):
                break

            # Step forward to consider the overlap
            i += self.unit - self.overlap

        return doc