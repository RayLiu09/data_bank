#-*- coding: utf-8 -*-
import logging

from capsules.authorization.models.claim import CapsuleClaimModel
from capsules.authorization.schema import CapsuleClaim
from common.db_deps import SessionDep


class CapsuleClaimRepository:
    def __init__(self):
        pass

    async def create_capsule_claim(self, db: SessionDep, capsule_claim_in: CapsuleClaimModel, signature: str) -> CapsuleClaim:
        """
        存储1阶胶囊授权指令到数据库
        """
        db_capsule_claim = CapsuleClaim(**capsule_claim_in.model_dump(exclude_unset= True))
        db_capsule_claim.authorizer_signature = signature
        db.add(db_capsule_claim)
        db.commit()
        db.refresh(db_capsule_claim)
        return db_capsule_claim
    async def get_capsule_claim(self, db: SessionDep, capsule_claim_uuid: str):
        return db.query(CapsuleClaim).filter(CapsuleClaim.uuid == capsule_claim_uuid).first()

capsule_claim_repo = CapsuleClaimRepository()