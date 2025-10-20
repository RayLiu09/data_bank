# -*- coding: utf-8 -*-
import logging
import hmac

import Crypto
from Crypto.Hash import SHA512, Poly1305

logger = logging.getLogger(__name__)

class HMACUtil:
    """
    HMACUtil类，用于计算HMAC-SHA-512和Poly1305哈希值
    """

    @staticmethod
    def hmac_sha512(message: str, key: str) -> str:
        """
        计算HMAC-SHA-512哈希值, HAMC-SHA512是一种对称密码学技术，使用同一个密钥进行签名和验证，发送方和接收方必须共享同一个密钥。

        Args:
            message: 待计算哈希值的字符串
            key: 对称加密密钥字符串

        Returns:
            str: HMAC-SHA-512哈希值
        """
        logger.debug(f"Hashing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        return hmac.new(key.encode('utf-8'), message.encode('utf-8'), SHA512).hexdigest()

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
        cipher = Crypto.Cipher.ChaCha20.new(key=key.encode('utf-8'), nonce=nonce.encode('utf-8'))
        mac = Poly1305.new(key=key.encode('utf-8'), cipher=cipher)
        mac.update(message.encode('utf-8'))
        return mac.hexdigest()