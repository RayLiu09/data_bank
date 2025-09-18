import logging
from typing import Any

from sqlalchemy import Sequence, select, delete, or_, column, func
from sqlalchemy.orm import Session

from kb.dbschema import KBGraphNode, KBGraph
from kb.models.kbgraphnode import KBGraphNodeCreate
from kb.respository.kbgraph import kbgraph_repo

logger = logging.getLogger(__name__)

def _has_exists(name, nodes):
    for item in nodes:
        if item["name"] == name:
            return True
    return False


def _build_tree_nodes(node: str, level: int, kbgraph_nodes: Sequence[KBGraphNode]) -> Any:
    root = {
        "name": node,
        "value": "",
        "level": level,
        "children": [
        ]
    }

    # Construct 1rst level
    for item in kbgraph_nodes:
        node = {
            "name": item.level_1,
            "value": "",
            "level": level + 1,
            "children": [
            ]
        }
        if not _has_exists(item.level_1, root["children"]):
            root["children"].append(node)

    # Construct 2cnd level
    for children in root["children"]:
        for item in kbgraph_nodes:
            if item.level_1 == children["name"]:
                node = {
                    "name": item.level_2,
                    "value": "",
                    "level": level + 2,
                    "children": [
                    ]
                }
                if not _has_exists(item.level_2, children["children"]):
                    children["children"].append(node)
    # Construct 3rd level
    for children in root["children"]:
        for children2 in children["children"]:
            for item in kbgraph_nodes:
                if item.level_1 == children["name"] and item.level_2 == children2["name"]:
                    node = {
                        "name": item.level_3,
                        "value": item.content if item.level_4 == "" else "",
                        "level": level + 3,
                        "children": [
                        ]
                    }
                    if not _has_exists(item.level_3, children2["children"]):
                        children2["children"].append(node)
    # Construct 4th level
    for children in root["children"]:
        for children2 in children["children"]:
            for children3 in children2["children"]:
                for item in kbgraph_nodes:
                    if item.level_1 == children["name"] and item.level_2 == children2["name"] and \
                            item.level_3 == children3["name"] and item.level_4 != "":
                        node = {
                            "name": item.level_4,
                            "value": item.content,
                            "level": level + 4,
                            "children": [
                            ]
                        }
                        children3["children"].append(node)
    return root

class KBGraphNodeRepository:
    """知识图谱节点"""
    def __init__(self):
        pass

    async def create_kbgraph_node(self, db: Session, kbgraph_node_list: list[KBGraphNodeCreate]):
        """
        Create KBGraphNode object in batch.
        """
        for kbgraph_node_in in kbgraph_node_list:
            db_kbgraph_node = KBGraphNode(**kbgraph_node_in.model_dump(exclude_unset=True))
            db.add(db_kbgraph_node)
        db.commit()

        return True

    async def count_kbgraph_nodes(self, db: Session, kbgraph_id: int) -> int:
        """
        Fetch the total number of KBGraphNode objects belong to a KBGraph object
        """
        return db.query(KBGraphNode).where(KBGraphNode.kbgraph_id == kbgraph_id).count()

    async def list_kbgraph_nodes(self, db: Session, kbgraph_id: int, in_tree_mode: bool = False,
                           skip: int = 0, limit: int = 1000) -> dict[
        str, int | Sequence[KBGraphNode]]:
        """
        List all KBGraphNode objects
        """
        kbgraph = db.get(KBGraph, kbgraph_id)
        if kbgraph is None:
            return {"count": 0, "kbgraph_nodes": []}
        statement = select(KBGraphNode).where(KBGraphNode.kbgraph_id == kbgraph_id).offset(skip).limit(limit)
        kbgraph_nodes = db.execute(statement).all()
        if in_tree_mode:
            return _build_tree_nodes(kbgraph.name, 0, kbgraph_nodes)
        return {"count": self.count_kbgraph_nodes(db, kbgraph_id), "kbgraph_nodes": kbgraph_nodes}

    async def fetch_kbgraph_nodes(self, db: Session, kbgraph_name: str, level_1: str = None, level_2: str = None,
                            level_3: str = None,
                            level_4: str = None) -> Sequence[KBGraphNode]:
        """
        Fetch KBGraphNode objects by kbgraph_name, level_1, level_2, level_3, level_4

        Parameters:
              @db: Session, Database session
              @kbgraph_name: str, the book name
              @level_1: str, the chapter name
              @level_2: str, the section name
              @level_3: str, the subsection name
              @level_4: str, the knowledge name
        """
        statement = select(KBGraphNode).join(KBGraph).where(KBGraph.name == kbgraph_name)
        logger.info("Fetch KBGraphNode objects by %s", statement)
        if level_1:
            statement = statement.where(column(KBGraphNode.level_1).like(f"%{level_1}%"))
        if level_2:
            statement = statement.where(column(KBGraphNode.level_2).like(f"%{level_2}%"))
        if level_3:
            statement = statement.where(column(KBGraphNode.level_3).like(f"%{level_3}%"))
        if level_4:
            statement = statement.where(column(KBGraphNode.level_4).like(f"%{level_4}%"))
        return db.execute(statement).all()

    async def search_kbgraph_nodes(self, db: Session, knowledge_name: str) -> Sequence[KBGraphNode]:
        """
        Search KBGraphNode objects by knowledge base

        Parameters:
            @knowledge_name: str, knowledge for search

        """
        statement = select(KBGraphNode)
        if knowledge_name:
            statement = statement.where(or_(column(KBGraphNode.level_3).like(f"%{knowledge_name}%"),
                                            column(KBGraphNode.level_4).like(f"%{knowledge_name}%")))

        return db.execute(statement).all()

    async def search_kbgraph_nodes_by_level(self, db: Session, search_keyword: str, level: int = 1) -> Sequence[KBGraphNode]:
        """
        Search KBGraphNode objects by level and search keyword
        """
        statement = select(KBGraphNode)
        if level == 1:
            statement = statement.where(column(KBGraphNode.level_1).like(f"%{search_keyword}%"))
        elif level == 2:
            statement = statement.where(column(KBGraphNode.level_2).like(f"%{search_keyword}%"))
        elif level == 3:
            statement = statement.where(column(KBGraphNode.level_3).like(f"%{search_keyword}%"))
        elif level == 4:
            statement = statement.where(column(KBGraphNode.level_4).like(f"%{search_keyword}%"))
        else:
            pass
        return db.execute(statement).all()

    async def search_kbgraph_nodes_with_book(self, db: Session, knowledge_name: str):
        """
        Search KBGraphNode objects by knowledge base

        Parameters:
            @knowledge_name: str, knowledge for search

        """
        statement = select(KBGraphNode, KBGraph).join(KBGraph, KBGraph.id == KBGraphNode.kbgraph_id)
        if knowledge_name:
            statement = statement.where(or_(column(KBGraphNode.level_3).like(f"%{knowledge_name}%"),
                                            column(KBGraphNode.level_4).like(f"%{knowledge_name}%")))

        all_knowledges = db.execute(statement).all()
        all_returns = []
        for item in all_knowledges:
            all_returns.append({
                "book": item.KBGraph.name,
                "chapter": item.KBGraphNode.level_1,
                "section": item.KBGraphNode.level_2,
                "subsection": item.KBGraphNode.level_3,
                "knowledge": item.KBGraphNode.level_4,
                "content": item.KBGraphNode.content
            })

        return all_returns

    async def del_kbgraph_node(self, db: Session, kbgraph_id: int):
        """
        Delete kbgraph nodes by kbgraph id
        """
        statement = delete(KBGraphNode).where(KBGraphNode.kbgraph_id == kbgraph_id)
        db.execute(statement)
        db.commit()
        # Delete parent node
        return kbgraph_repo.del_kbgraph(db, kbgraph_id)


kbgraph_node_repo = KBGraphNodeRepository()