# -*- coding: utf-8 -*-
import logging

from Crypto.Hash import SHA512, SHA384

logger = logging.getLogger(__name__)

class HashUtil:
    """
    HashUtil类，用于计算SHA-512, SHA-384, HMAC和Poly1305哈希值, 注意：SHA-224, SHA256和SHA512都易于收到length-extension attacks,不建议用于哈希敏感信息
    """
    @staticmethod
    def sha512(message: str) -> str:
        """
        计算SHA-512哈希值

        Args:
            message: 待计算哈希值的字符串

        Returns:
            str: SHA-512哈希值
        """
        logger.debug(f"Hashing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        return SHA512.new(message.encode('utf-8')).hexdigest()

    @staticmethod
    def sha384(message: str) -> str:
        """
        计算SHA-384哈希值

        Args:
            message: 待计算哈希值的字符串

        Returns:
            str: SHA-384哈希值
        """
        logger.debug(f"Hashing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        return SHA384.new(message.encode('utf-8')).hexdigest()
