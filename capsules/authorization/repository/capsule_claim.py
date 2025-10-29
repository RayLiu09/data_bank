#-*- coding: utf-8 -*-
import json
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
        if capsule_claim_in.scope:
            logger.info(f"Create capsule claim scope: {capsule_claim_in.scope}")
            print(f"************{capsule_claim_in.scope}************")
            db_capsule_claim.scope = json.dumps({"basic_data": capsule_claim_in.scope.basic_data, "zkp_data": capsule_claim_in.scope.zkp_data})
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

    async def list_capsule_claims_by_owner(self, db: SessionDep, owner: str,  offset: int = 0, limit: int = 10):
        """
        列出1阶胶囊授权指令
        """
        logger.info(f"List capsule claims by owner")
        db_capsule_claims = db.query(CapsuleClaim).filter(CapsuleClaim.authorizer == owner).offset(offset).limit(limit).all()
        logger.info(f"List capsule claims successfully: {db_capsule_claims}")
        return db_capsule_claims

    async def list_capsule_claims_by_receiver(self, db: SessionDep, receiver: str,  offset: int = 0, limit: int = 10):
        """
        列出1阶胶囊授权指令
        """
        logger.info(f"List capsule claims by receiver")
        db_capsule_claims = db.query(CapsuleClaim).filter(CapsuleClaim.receiver == receiver).offset(offset).limit(limit).all()
        logger.info(f"List capsule claims successfully: {db_capsule_claims}")
        return db_capsule_claims

    async def list_capsule_claims(self, db: SessionDep, offset: int = 0, limit: int = 10):
        """
        列出1阶胶囊授权指令
        """
        logger.info(f"List capsule claims")
        db_capsule_claims = db.query(CapsuleClaim).offset(offset).limit(limit).all()
        logger.info(f"List capsule claims successfully: {db_capsule_claims}")
        return db_capsule_claims

capsule_claim_repo = CapsuleClaimRepository()