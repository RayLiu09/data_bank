# -*- coding: utf-8 -*-
import logging

from sqlmodel import Session

from pki.kms import SecretKey
from pki.kms.key_model import KeyModel


class KeyRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("KeyRepository init")

    async def get_key(self, db: Session, key_uuid: str) -> SecretKey:
        """
        根据key_id获取密钥
        :param db
        :param key_uuid:
        :return:
        """
        self.logger.info(f"get_key key_id: {key_uuid}")

        return db.query(SecretKey).filter(SecretKey.uuid == key_uuid).first()

    async def create_key(self, db: Session, key: KeyModel) -> SecretKey:
        """
        创建密钥
        :param db
        :param key:
        :return:
        """
        self.logger.info(f"create_key key: {key}")
        key_create = key.model_dump(exclude_unset=True)
        db.add(key_create)
        db.commit()
        db.refresh(key_create)

        return key_create

key_repository = KeyRepository()