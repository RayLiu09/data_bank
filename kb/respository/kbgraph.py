from typing import Any

from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session

from kb.dbschema import KBGraph
from kb.models.kbgraph import KBGraphCreate


class KBGraphRepository:
    def __init__(self):
        pass

    async def create_kbgraph(self, db: Session, kbgraph_in: KBGraphCreate) -> KBGraph:
        """
        Create a KBGraph object
        """
        db_kbgraph = KBGraph(**kbgraph_in.model_dump(exclude_unset=True))
        db.add(db_kbgraph)
        db.commit()
        db.refresh(db_kbgraph)
        return db_kbgraph

    async def count_kbgraph(self, db: Session) -> int:
        return db.query(KBGraph).count()

    async def list_kbgraphs(self, db: Session, skip: int = 0, limit: int = 1000) -> dict[str, Any]:
        """
        List all KBGraph objects
        """
        statement = select(KBGraph).offset(skip).limit(limit).order_by(KBGraph.create_time.desc())
        kbgraphs = db.execute(statement).all()
        count = await self.count_kbgraph(db)
        return {"count": count , "kbgraphs": kbgraphs}

    async def del_kbgraph(self, db: Session, kbgraph_id: int):
        """
        Delete kbgraph by id.
        """
        kbgraph = db.query(KBGraph).get(kbgraph_id)
        if kbgraph:
            db.delete(kbgraph)
            db.commit()
        return kbgraph

kbgraph_repo = KBGraphRepository()