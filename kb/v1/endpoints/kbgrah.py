import logging
import os
from http import HTTPStatus
from typing import List, Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Path, File

from common.db_deps import SessionDep
from common.response_util import response_base
from kb.models.kbgraph import KBGraphCreate
from kb.models.kbgraphnode import KBGraphNodeCreate
from kb.respository.kbgraph import kbgraph_repo
from kb.respository.kbgraphnode import kbgraph_node_repo
from common.constants import FILE_SIZE_200MB
from kb.utils.graph_builder import build_kbgraph
from security.token_deps import TokenDeps

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list", dependencies=[TokenDeps], summary="List all kbgraphs")
async def list_kbgraphs(db: SessionDep, skip: int = 0, limit: int = 1000):
    """
    Fetch all kbgraphs
    """
    all_kbgraphs = await kbgraph_repo.list_kbgraphs(db, skip=skip, limit=limit)

    return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=all_kbgraphs)



@router.get("/nodes/{kbgraph_id}", dependencies=[TokenDeps], summary="List all kbgraph nodes by kbgraph id")
async def list_kbgraph_nodes(db: SessionDep, kbgraph_id: Annotated[int, Path(title="知识图谱ID", gt=0)], in_tree_mode: bool = False, skip: int = 0, limit: int = 1000):
    """
    Fetch all kbgraph nodes
    """
    all_kbgraph_nodes = await kbgraph_node_repo.list_kbgraph_nodes(db, kbgraph_id=kbgraph_id, in_tree_mode=in_tree_mode, skip=skip,
                                              limit=limit)
    return response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=all_kbgraph_nodes)


@router.get("/chapters", dependencies=[TokenDeps], summary="List all kbgraph chapters")
async def list_kbgraph_chapters(db: SessionDep, kbgraph_id: int) -> List[str]:
    """
    Get all kbgraph chapters, level_1
    """
    chapters = []
    ret = await kbgraph_node_repo.list_kbgraph_nodes(db, kbgraph_id=kbgraph_id)
    print(ret["kbgraph_nodes"])
    if ret:
        all_nodes = ret["kbgraph_nodes"]

        for node in all_nodes:
            if node.level_1 not in chapters:
                chapters.append(node.level_1)

    return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=chapters)


@router.post("/", dependencies=[TokenDeps], summary="Create a kbgraph by uploaded file")
async def create_kbgraph(file: Annotated[UploadFile, File(title="上传用于构建知识图谱的源文件", description="知识图谱源数据文件")], db: SessionDep):
    """
    Create a kbgraph by uploaded file
    """
    if file is None:
        raise HTTPException(status_code=400, detail="File is required")

    if file.content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raise HTTPException(status_code=400, detail="File type must be .docx")

    if file.size > FILE_SIZE_200MB:
        raise HTTPException(status_code=400, detail="File size must be less or equal than 200MB")

    file_path = f"{os.getenv('UPLOAD_DIR')}/{file.filename}"
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file=file_path, mode="wb") as buffer:
        while content := await file.read(1024):
            buffer.write(content)

    kb_nodes = await build_kbgraph(file_path)

    if len(kb_nodes) == 0:
        logger.info("KBGraph is empty")
        raise HTTPException(status_code=400, detail="Uploaded docx is not in valid format, such as h1, h2, h3 and h4.")

    kb_graph_create = KBGraphCreate(name=file.filename.split(".")[0], group="default", description="auto generated kbgraph")
    kb_graph = await kbgraph_repo.create_kbgraph(db, kb_graph_create)

    kb_graph_node_list = []
    for kb_node in kb_nodes:
        kb_node_create = KBGraphNodeCreate(kbgraph_id=kb_graph.id, **kb_node)
        kb_graph_node_list.append(kb_node_create)

    await kbgraph_node_repo.create_kbgraph_node(db, kb_graph_node_list)

    return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=kb_graph)


@router.get("/nodes", dependencies=[TokenDeps], summary="Fetch kbgraph nodes by kbgraph name")
async def fetch_kbgraph_nodes(db: SessionDep, kbgraph_name: str):
    """
    Fetch kbgraph nodes by kbgraph name
    """
    all_kbgraph_nodes = await kbgraph_node_repo.fetch_kbgraph_nodes(db, kbgraph_name=kbgraph_name)
    return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=all_kbgraph_nodes)


@router.delete("/nodes/{id}", dependencies=[TokenDeps], summary="Delete kbgraph node by id")
async def del_kbgraph_node(db: SessionDep, id: int):
    """
    Delete kbgraph node by id
    """
    return await kbgraph_node_repo.del_kbgraph_node(db, kbgraph_id=id)

@router.get("/search", dependencies=[TokenDeps], summary="Search kbgraph nodes by name")
async def search_kbgraph_nodes(db: SessionDep, knowledge_name: str):
    """
    Args:
        db: Database session
        knowledge_name: the query key used for fetching knowledge nodes
        current_user:

    Returns:
        All matched knowledge nodes
    """
    all_kbgraphs = await kbgraph_node_repo.search_kbgraph_nodes_with_book(db, knowledge_name=knowledge_name)
    return await response_base.success_simple(code=HTTPStatus.OK, msg='Success', data=all_kbgraphs)