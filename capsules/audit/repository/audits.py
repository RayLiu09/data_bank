import logging
from typing import Any

from sqlalchemy.orm import Session

from capsules.audit.schema import AuditLog

logger = logging.getLogger(__name__)

class AuditRepository:
    """
    审计仓库，用于存储审计信息
    """
    def __init__(self):
        pass

    async def save_audit(self, db: Session, audit_info: dict) -> AuditLog:
        """
        保存审计信息

        Args:
            audit_info: 审计信息
        """
        # 保存审计信息到数据库或其他存储位置
        audit_info = AuditLog(**audit_info)
        db.add(audit_info)
        db.commit()
        db.refresh(audit_info)
        return audit_info

    async def get_audit(self, db: Session, audit_id: str) -> Any:
        """
        获取审计信息

        Args:
            audit_id: 审计ID

        Returns:
            dict: 审计信息
        """
        audit = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
        if not audit:
            logger.info(f"No audit found with id {audit_id}")
            return {}
        return audit

    async def list_audits(self, db: Session, offset: int = 0, limit: int = 10) -> list:
        """
        获取审计列表

        Args:
            offset: 偏移量
            limit: 页大小

        Returns:
            list: 审计列表
        """
        audits = db.query(AuditLog).offset(offset).limit(limit).all()
        if not audits:
            logger.info("No audits found")
            return []
        return [audit.to_dict for audit in audits]

audit_repository = AuditRepository()