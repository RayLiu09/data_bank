# -*- coding:utf-8 -*-
import logging

from capsules.authorization.repository.capsule_claim import capsule_claim_repo
from common.db_deps import SessionDep

logger = logging.getLogger(__name__)

class ClaimService:
    def __init__(self):
        pass

    async def list_claims(self, db: SessionDep, offset: int = 0, limit: int = 10):
        """
        List claims
        """
        return await capsule_claim_repo.list_capsule_claims(db, offset, limit)

    async def get_claims_by_owner(self, db: SessionDep, owner: str, offset: int = 0, limit: int = 10):
        """
        Get claims by owner
        """
        return await capsule_claim_repo.get_claims_by_owner(db, owner, offset, limit)

    async def get_claims_by_receiver(self, db: SessionDep, receiver: str, offset: int = 0, limit: int = 10):
        """
        Get claims by receiver
        """
        return await capsule_claim_repo.get_claims_by_receiver(db, receiver, offset, limit)

claim_srv = ClaimService()