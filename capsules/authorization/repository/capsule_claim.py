#-*- coding: utf-8 -*-
import logging

from capsules.authorization.models.claim import CapsuleClaimModel
from capsules.authorization.schema import CapsuleClaim
from common.db_deps import SessionDep

logger = logging.getLogger(__name__)

class CapsuleClaimRepository:
    def __init__(self):
        pass

    async def create_capsule_claim(self, db: SessionDep, capsule_claim_in: CapsuleClaimModel, signature: str) -> CapsuleClaim:
        """
        存储1阶胶囊授权指令到数据库
        """
        logger.info(f"Create capsule claim: {capsule_claim_in}")
        db_capsule_claim = CapsuleClaim(**capsule_claim_in.model_dump(exclude_unset= True))
        db_capsule_claim.authorizer_signature = signature
        db.add(db_capsule_claim)
        db.commit()
        db.refresh(db_capsule_claim)
        logger.info(f"Create capsule claim successfully: {db_capsule_claim}")
        return db_capsule_claim

    async def get_capsule_claim(self, db: SessionDep, capsule_claim_uuid: str):
        return db.query(CapsuleClaim).filter(CapsuleClaim.uuid == capsule_claim_uuid).first()

    async def deprecate_capsule_claim(self, db: SessionDep, capsule_claim_uuid: str):
        """
        删除1阶胶囊授权指令
        """
        logger.info(f"Deprecate capsule claim: {capsule_claim_uuid}")
        db_capsule_claim = db.query(CapsuleClaim).filter(CapsuleClaim.uuid == capsule_claim_uuid).first()
        if db_capsule_claim:
            # 更新deprecated字段为1
            db_capsule_claim.deprecated = 1
            db.commit()
            db.refresh(db_capsule_claim)
            logger.info(f"Deprecate capsule claim successfully: {db_capsule_claim}")
            return True
        else:
            logger.warning(f"Deprecate capsule claim failed: {capsule_claim_uuid}")
            return False

capsule_claim_repo = CapsuleClaimRepository()