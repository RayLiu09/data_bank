#-*- coding:utf-8 -*-
import logging

from capsules.audit.repository.audits import audit_repository
from common.bus_exception import BusException

logger = logging.getLogger(__name__)

class AuditSrv:
    def __init__(self):
        pass
    async def list_audits(self, db, offset, limit):
        """
        List data capsule audits
        """
        try:
            audits = await audit_repository.list_audits(db, offset, limit)
            return audits
        except Exception as e:
            logger.error(f"List data capsule audits failed: {str(e)}")
            raise BusException(code=50001, message=f"获取数据胶囊审计日志失败: {str(e)}")

audit_srv = AuditSrv()