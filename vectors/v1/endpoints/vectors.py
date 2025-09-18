# encoding: utf-8
"""
@File    :   vectors.py
@Time    :   2023/06/01 09:09:09
@Version :   1.0
@Desc    :   vectors include all endpoints for vector operations.
"""
import logging
import os

from fastapi import APIRouter, UploadFile, Depends, HTTPException

from common.background_task import background_task
from common.constants import FILE_SIZE_200MB, ALLOWED_FILE_TYPES
from security.token_deps import TokenDeps
from vectors.data_loader import DataLoader
from vectors.retrievers.weaviate_retriever import WeaviateRetriever

logger: logging.Logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", dependencies=[TokenDeps], summary="Upload a document to the vector store.")
async def upload_doc(files: list[UploadFile]):
    """
    Endpoint for uploading a document to the vector store.

    Parameters:
        files(UploadFile): the uploaded files

    Returns:
        dict: A response containing the file name and a success message.
    """
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    for file in files:
        # Get the file extension to check if it's allowed
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400,
                                detail=f"File type not allowed. Allowed types: {ALLOWED_FILE_TYPES}")
        if file is not None and file.size > FILE_SIZE_200MB:  # 200MB
            logger.info(f"File size exceeds the limit of 200MB. File: {file.filename}")
            continue
        # Obtain the default upload directory
        file_path = f"{os.getenv('UPLOAD_DIR')}/{file.filename}"
        with open(file_path, "wb") as buffer:
            while content := await file.read(1024):
                buffer.write(content)

        # Start the background task for processing the file
        background_thread = background_task(
            "Vectorize Doc Task",
            task_func=DataLoader().load,
            file_name=file_path
        )

    return {"message": "File uploaded successfully, and it would be processed in the background."}


@router.get("/list", dependencies=[TokenDeps], summary="List all documents in the vector store.")
async def get_documents(offset: int = 0, limit: int = 10):
    """
    Endpoint for retrieving documents from the vector store.

    Parameters:
        offset(int): the offset for pagination
        limit(int): the limit for pagination

    Returns:
        dict: A response containing the documents and a success message.
    """
    docs = await WeaviateRetriever().list_all_docs(offset=offset, limit=limit)

    return docs


@router.get("/chunks/list", dependencies=[TokenDeps], summary="List all chunks in the vector store.")
async def get_documents_chunks(uuid: str, offset: int = 0, limit: int = 10):
    """
    Endpoint for retrieving documents from the vector store.

    Parameters:
        offset(int): the offset for pagination
        limit(int): the limit for pagination

    Returns:
        dict: A response containing the documents and a success message.
    """
    if not uuid:
        raise HTTPException(status_code=400, detail="uuid is required.")

    chunks = await WeaviateRetriever().list_all_chunks_by_doc_uuid(uuid=uuid, offset=offset, limit=limit)

    return chunks


@router.delete("/delete/{uuid}", dependencies=[TokenDeps], summary="Delete document from the vector store.")
async def delete_documents(uuid: str):
    """
    Endpoint for delete document from the vector store.

    Parameters:
        uuid(str): the uuid of the document

    Returns:
        bool: False or True
    """
    if not uuid:
        raise HTTPException(status_code=400, detail="uuid is required.")

    is_ok = await WeaviateRetriever().del_document_by_uuid(uuid=uuid)

    return is_ok


@router.delete("/chunk/delete/{uuid}", dependencies=[TokenDeps], summary="Delete chunk from the vector store.")
async def delete_chunk_by_uuid(uuid: str):
    """
    Endpoint for delete chunk from the vector store.

    Parameters:
        uuid(str): the uuid of the chunk

    Returns:
        bool: False or True
    """
    if not uuid:
        raise HTTPException(status_code=400, detail="uuid is required.")

    is_ok = await WeaviateRetriever().del_chunk_by_uuid(uuid=uuid)

    return is_ok


@router.get("/chunk/search", dependencies=[TokenDeps], summary="Similarity search in the vector store.")
async def similarity_search(query: str, top_k: int = 5):
    """
    Endpoint for similarity search in the vector store.

    Parameters:
        query(str): the query string
    Returns:
        list(dict): A list of chunks
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")

    chunks = await WeaviateRetriever().similarity_search(query=query, top_k=top_k)

    return chunks
