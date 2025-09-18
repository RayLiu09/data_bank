import logging

import spacy

from vectors.chunkings.base_chunking import BaseChunking
from vectors.models.chunk import Chunk
from vectors.models.document import Document

logger = logging.getLogger(__name__)


class SentenceChunking(BaseChunking):
    """
    A chunking class for splitting text into sentences.
    """

    def __init__(self, unit: int, overlap: int, **kwargs):
        super().__init__()
        self.name = "SentenceChunking"
        self.unit = unit | 5
        self.overlap = overlap | 1
        self.description = "A chunking class for splitting text into sentences."
        self.nlp = spacy.blank("zh")
        self.nlp.add_pipe("sentencizer")

    def chunk_data(self, doc: Document) -> Document:
        """
        Chunk the data into sentences.
        And based-up on the unit and overlap, each chunk includes number of unit sentences.
        There is overlap between each chunk.
        """
        if len(doc.chunks) > 0:
            logger.info("Chunks already exist. Skipping chunking.")
            return doc

        sentences = list(self.nlp(doc.content).sents)
        if self.unit > len(sentences):
            logger.info("Unit is greater than the number of sentences. Skipping chunking.")
            return doc

        i = 0
        spliter_id = 0
        while i < len(sentences):
            start_i = i
            end_i = i + self.unit
            if end_i > len(sentences):
                end_i = len(sentences)

            text = ""
            for sent in sentences[start_i:end_i]:
                text += sent.text

            doc_chunk = Chunk(
                doc_name=doc.name,
                content=text,
                chunk_id=spliter_id
            )
            doc.chunks.append(doc_chunk)
            spliter_id += 1

            # Exit loop if this is the last chunk
            if end_i == len(sentences):
                break

            # Step forward to consider the overlap
            i += self.unit - self.overlap

        return doc