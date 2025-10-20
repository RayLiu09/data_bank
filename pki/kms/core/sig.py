import logging
import os

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

logger = logging.getLogger(__name__)

class DigitalSignature:
    def __init__(self, key_len: int = 2048):
        self.key_len = key_len

    @staticmethod
    def sign(message: str, pri_key: str) -> bytes:
        """
        使用签名者的私钥进行签名

        Args:
            message: str, 代签名的原始消息
            pri_key: RSA.RsaKey， 签名用私钥
        签名思路：使用基于PKI的公钥签名算法，即PKI with RSA PSS
        Returns:
            返回签名结果
        """
        logger.debug(f"Signing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        # 检查私钥是否为系统文件
        if os.path.exists(pri_key):
           pri_key = open(pri_key).read()
        rsa_key = RSA.import_key(pri_key)
        alg_hash = SHA512.new()
        alg_hash.update(message.encode('utf-8'))
        logger.debug(f"Hash: {alg_hash.hexdigest()}")
        # 数字签名要携带时间戳和位置信息
        # alg_hash.update(f"{message}{time.time()}{os.getpid()}".encode('utf-8'))
        return pss.new(rsa_key).sign(alg_hash)

    @staticmethod
    def verify(message: str, signature: bytes, pub_key: str) -> bool:
        """
        验证签名

        Args:
            message: str, 待验证的消息内容
            signature: bytes, 待验证的签名
            pub_key: RSA.RsaKey, 验证用公钥

        Returns:
            bool: 验证结果
        """
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        if os.path.exists(pub_key):
           pub_key = open(pub_key).read()
        rsa_key = RSA.import_key(pub_key)
        alg_hash = SHA512.new(message.encode('utf-8'))
        verifier = pss.new(rsa_key)

        try:
            verifier.verify(alg_hash, signature)
            return True
        except ValueError:
            return False