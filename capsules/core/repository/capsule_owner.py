# -*- coding: utf-8 -*-
import logging

from capsules.core.schema import CapsuleOwner
from common.db_deps import SessionDep

logger = logging.getLogger(__name__)

class CapsuleOwnerRepository:
    def __init__(self):
        pass

    async def save_capsule_owner(self, db: SessionDep, capsule_owner: dict):
        """
        Save capsule owner
        """
        capsule_owner_in_db = CapsuleOwner(**capsule_owner)
        db.add(capsule_owner_in_db)
        db.commit()
        db.refresh(capsule_owner_in_db)
        return capsule_owner_in_db

capsule_owner_repo = CapsuleOwnerRepository()