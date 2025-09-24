# -*- coding: utf-8 -*-
from Crypto.Hash import SHA512, SHA384, HMAC, Poly1305
import logging

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

    @staticmethod
    def hmac_sha512(message: str, key: str) -> str:
        """
        计算HMAC-SHA-512哈希值

        Args:
            message: 待计算哈希值的字符串
            key: 密钥字符串

        Returns:
            str: HMAC-SHA-512哈希值
        """
        logger.debug(f"Hashing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        return HMAC.new(key.encode('utf-8'), message.encode('utf-8'), SHA512).hexdigest()

    @staticmethod
    def poly1305(message: str, key: str, nonce: str) -> str:
        """
        计算Poly1305哈希值

        Args:
            message: 待计算哈希值的字符串
            key: 密钥字符串
            nonce: 随机数字符串

        Returns:
            str: Poly1305哈希值
        """
        logger.debug(f"Hashing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if not isinstance(nonce, str):
            raise TypeError("Nonce must be a string")
        return Poly1305.new(key.encode('utf-8'), message.encode('utf-8'), nonce.encode('utf-8')).hexdigest()