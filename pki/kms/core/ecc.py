import logging
import os

from Crypto.Hash import SHA512
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

logger = logging.getLogger(__name__)


class ECCAlgorithm:
    """
    ECC算法类，用于进行ECC密钥对生成，数字签名和验证
    """
    @staticmethod
    def generate_keypair(curve: str = "ed25519") -> ECC.EccKey:
        """
        生成ECC(Elliptic Curve Cryptography)算法类型的密钥对

        Args:
            curve: str,指定曲线类型,ED系列：ed25519 | ed448
        """
        return ECC.generate(curve=curve)

    @staticmethod
    def digital_sign(message: str, pri_key: str) -> bytes:
        """
        使用签名者的私钥进行签名

        Args:
            message: str, 待签名的消息内容
            pri_key: ECC.EccKey， 签名用私钥

        Returns:
            返回签名结果
        """
        logger.debug(f"Signing message: {message}")
        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        # 检查私钥是否为系统文件
        if os.path.exists(pri_key):
            pri_key = open(pri_key).read()
        try:
            pri_key_instance = ECC.import_key(pri_key)
        except ValueError:
            raise ValueError("Invalid private key")
        alg_hash = SHA512.new()
        alg_hash.update(message.encode('utf-8'))
        logger.debug(f"Hash: {alg_hash.hexdigest()}")

        # 采用Ed25519椭圆曲线算法进行签名
        return eddsa.new(pri_key_instance, mode="rfc8032").sign(alg_hash)

    @staticmethod
    def verify_signature(message: str, signature: bytes, pub_key: str):
        """
        验证签名

        Args:
            message: str, 待验证的消息内容
            signature: bytes, 待验证的签名
            pub_key: ECC.EccKey, 验证用公钥
        """

        if not isinstance(message, str):
            raise TypeError("Message must be a string")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        if os.path.exists(pub_key):
            pub_key = open(pub_key).read()
        try:
            pub_key_instance = ECC.import_key(pub_key)
        except ValueError:
            raise ValueError("Invalid public key")
        alg_hash = SHA512.new()
        alg_hash.update(message.encode('utf-8'))
        logger.debug(f"Hash: {alg_hash.hexdigest()}")

        eddsa.new(pub_key_instance, mode="rfc8032").verify(signature, message.encode('utf-8'))
