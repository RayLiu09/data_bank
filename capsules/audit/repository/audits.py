from sqlalchemy.orm import Session

from capsules.audit.schema import AuditLog


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

    async def get_audit(self, db: Session, audit_id: str) -> dict:
        """
        获取审计信息

        Args:
            audit_id: 审计ID

        Returns:
            dict: 审计信息
        """
        # TODO: 从数据库或其他存储位置获取审计信息
        return {}

audit_repository = AuditRepository()