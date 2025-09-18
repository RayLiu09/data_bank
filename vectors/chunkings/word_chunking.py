import logging

import spacy

from vectors.chunkings.base_chunking import BaseChunking
from vectors.models.chunk import Chunk
from vectors.models.document import Document

logger = logging.getLogger(__name__)


class WordChunking(BaseChunking):
    """
    A chunking class for splitting text into words.
    """

    def __init__(self, unit: int, overlap: int, **kwargs):
        super().__init__()
        self.name = "WordChunking"
        self.unit = unit | 300
        self.overlap = overlap | 20
        self.description = "A chunking class for splitting text into words."
        self.nlp = spacy.blank("zh")

    def chunk_data(self, doc: Document) -> Document:
        """
        Chunk the data into words.
        And based-up on the unit and overlap, each chunk includes number of unit words.
        There is overlap between each chunk.
        """
        if len(doc.chunks) > 0:
            logger.info("Chunks already exist. Skipping chunking.")
            return doc

        sDoc = self.nlp(doc.content)
        if self.unit > len(sDoc):
            logger.info("Unit is greater than the doc content. Skipping chunking.")
            doc_chunk = Chunk(
                doc_name=doc.name,
                content=sDoc.text,
                chunk_id=0
            )
            doc.chunks.append(doc_chunk)
            return doc

        i = 0
        spliter_id = 0
        while i < len(sDoc):
            start_i = i
            end_i = i + self.unit
            if end_i > len(sDoc):
                end_i = len(sDoc)

            text = ""
            for sent in sDoc[start_i:end_i]:
                text += sent.text

            doc_chunk = Chunk(
                doc_name=doc.name,
                content=text,
                chunk_id=spliter_id
            )
            doc.chunks.append(doc_chunk)
            spliter_id += 1

            # Exit loop if this is the last chunk
            if end_i == len(sDoc):
                break

            # Step forward to consider the overlap
            i += self.unit - self.overlap

        return doc