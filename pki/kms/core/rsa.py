# -*- coding: utf-8 -*-
import logging
import os
from hashlib import sha512

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

from settings import settings

logger = logging.getLogger(__name__)

class RSACipher:
    """
    RSA类，用于进行RSA公钥密码的加密和解密，以及数字签名的生成和验证

    其密码学安全性主要依赖于RSA模数n的大小，如最新最安全的3072
    """
    def __init__(self, key_len: int = 2048):
        self.key_len = key_len
        self.key_pair = RSA.generate(self.key_len)

    @staticmethod
    def generate_keypair(key_len: int = 2048) -> RSA.RsaKey:
        return RSA.generate(key_len)

    @staticmethod
    def generate_and_save_keypair(key_len: int = 2048, folder_path: str = settings.certs_dir) -> tuple[str, str]:
        """
        生成RSA密钥对，并将私钥和公钥以PEM格式存储到指定位置

        Args:
            key_len: 密钥长度，默认为2048
            folder_path: 存储密钥的文件夹路径

        Returns:
            tuple[str, str]: 私钥文件路径和公钥文件路径

        Raises:
            TypeError: 当输入参数类型不正确时
            ValueError: 当参数值无效时
            OSError: 当文件操作失败时
            Exception: 其他异常
        """
        try:
            # 参数类型检查
            if not isinstance(key_len, int):
                raise TypeError("Key length must be an integer")
            
            if not isinstance(folder_path, str):
                raise TypeError("Folder path must be a string")
            
            # 参数值验证
            if key_len < 1024:
                raise ValueError("Key length must be at least 1024 bits")
            
            if not folder_path:
                raise ValueError("Folder path cannot be empty")
            
            # 检查文件夹是否存在，不存在则创建
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            if not os.path.isdir(folder_path):
                raise ValueError("Folder path is not a valid directory")
            
            # 生成RSA密钥对
            key_pair = RSA.generate(key_len)
            
            # 导出私钥为PEM格式
            private_key_pem = key_pair.export_key(format="PEM", passphrase=settings.SECRET_PASSPHRASE, pkcs=8, protection="scryptAndAES128-CBC")
            
            # 导出公钥为PEM格式
            public_key_pem = key_pair.public_key().export_key()
            
            # 生成文件路径
            private_key_path = os.path.join(folder_path, "private_key.pem")
            public_key_path = os.path.join(folder_path, "public_key.pem")
            
            # 保存私钥到文件
            with open(private_key_path, "wb") as priv_file:
                priv_file.write(private_key_pem)
            
            # 保存公钥到文件
            with open(public_key_path, "wb") as pub_file:
                pub_file.write(public_key_pem)
            
            logger.info(f"RSA key pair generated and saved to {folder_path}")
            return private_key_path, public_key_path
            
        except TypeError as e:
            logger.error(f"Type error during key pair generation: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during key pair generation: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"OS error during key pair saving: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Key pair generation and saving failed: {str(e)}")
            raise

    @staticmethod
    def import_public_key(key_data: str) -> RSA.RsaKey:
        """
        导入公钥

        Args:
            key_data: 公钥数据（PEM格式的字符串）

        Returns:
            RSA.RsaKey: 导入的公钥对象

        Raises:
            TypeError: 当输入参数类型不正确时
            ValueError: 当密钥数据为空或格式不正确时
            Exception: 导入过程中出现的其他异常
        """
        try:
            if not isinstance(key_data, str):
                raise TypeError("Key data must be a string")
            
            if not key_data:
                raise ValueError("Key data cannot be empty")
            
            # 尝试导入公钥
            public_key = RSA.import_key(key_data)
            
            # 验证是否为有效的公钥（不包含私钥部分）
            if not public_key.has_public_key() or public_key.has_private():
                raise ValueError("Invalid public key data provided")
            
            return public_key
            
        except TypeError as e:
            logger.error(f"Type error during public key import: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during public key import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Public key import failed: {str(e)}")
            raise

    @staticmethod
    def import_private_key(key_data: str) -> RSA.RsaKey:
        """
        导入私钥

        Args:
            key_data: 私钥数据（PEM格式的字符串）

        Returns:
            RSA.RsaKey: 导入的私钥对象

        Raises:
            TypeError: 当输入参数类型不正确时
            ValueError: 当密钥数据为空或格式不正确时
            Exception: 导入过程中出现的其他异常
        """
        try:
            if not isinstance(key_data, str):
                raise TypeError("Key data must be a string")
            
            if not key_data:
                raise ValueError("Key data cannot be empty")
            
            # 尝试导入私钥
            private_key = RSA.import_key(key_data)
            
            # 验证是否为有效的私钥
            if not private_key.has_private():
                raise ValueError("Invalid private key data provided")
            
            return private_key
            
        except TypeError as e:
            logger.error(f"Type error during private key import: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during private key import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Private key import failed: {str(e)}")
            raise

    def digital_sign(self, message: str) -> str:
        """
        采用RSA公钥密码生成签名

        Args:
            message: 待进行签名的消息内容
        """

        hash_msg = int.from_bytes(sha512(self.str_to_buffer(message)).digest(), 'big')
        signature = pow(hash_msg, self.key_pair.d, self.key_pair.n)
        logger.debug(f"Signature: {signature}")
        return hex(signature)

    def verify_signature(self, message: str, signature: str) -> bool:
        """
        验证签名

        Args:
            message: 待验证的消息内容
            signature: 待验证的签名

        Returns:
            bool: 验证结果
        """
        hash_msg = int.from_bytes(sha512(self.str_to_buffer(message)).digest(), 'big')
        hash_from_signature = pow(hash_msg, self.key_pair.e, self.key_pair.n)
        logger.debug(f"Hash from signature: {hash_from_signature}, and original hash: {hash_msg}")
        return hash_from_signature == signature

    def str_to_buffer(self, text: str, encoding: str = 'utf-8') -> bytes:
        """
        将字符串转换为Buffer（bytes对象）

        Args:
            text: 要转换的字符串
            encoding: 字符串编码方式，默认为'utf-8'

        Returns:
            bytes: 转换后的字节序列（Buffer）
        """
        return text.encode(encoding)

    def encrypt_with_pubkey(self, message: bytes, pub_key: RSA.RsaKey) -> str:
        """
        使用外部公钥加密消息

        Args:
            message: 待加密的消息内容（bytes）
            pub_key: 用于加密的外部公钥

        Returns:
            str: Base64编码的加密消息

        Raises:
            TypeError: 当输入参数类型不正确时
            ValueError: 当消息为空或公钥无效时
            Exception: 加密过程中出现的其他异常
        """
        try:
            # 参数类型检查
            if not isinstance(message, bytes):
                raise TypeError("Message must be bytes")
            
            if not isinstance(pub_key, RSA.RsaKey) or not pub_key.has_public_key():
                raise TypeError("Invalid public key provided")
            
            if not message:
                raise ValueError("Message cannot be empty")
            
            # 检查消息长度是否超过RSA密文长度限制
            max_msg_len = pub_key.size_in_bytes() - 2 * 32 - 2  # OAEP填充的开销
            if len(message) > max_msg_len:
                raise ValueError(f"Message too long. Maximum length is {max_msg_len} bytes")
            
            # 使用PKCS1_OAEP进行加密
            cipher = PKCS1_OAEP.new(pub_key)
            ciphertext = cipher.encrypt(message)
            
            # 返回Base64编码的结果
            return base64.b64encode(ciphertext).decode('utf-8')
            
        except TypeError as e:
            logger.error(f"Type error during RSA encryption: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during RSA encryption: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_with_prikey(self, ciphertext: str, pri_key: RSA.RsaKey) -> bytes:
        """
        使用外部私钥解密消息

        Args:
            ciphertext: 待解密的消息内容（Base64编码的字符串）
            pri_key: 用于解密的外部私钥

        Returns:
            bytes: 解密后的消息内容

        Raises:
            TypeError: 当输入参数类型不正确时
            ValueError: 当密文为空或私钥无效时
            Exception: 解密过程中出现的其他异常
        """
        try:
            # 参数类型检查
            if not isinstance(ciphertext, str):
                raise TypeError("Ciphertext must be a base64 encoded string")
            
            if not isinstance(pri_key, RSA.RsaKey) or not pri_key.has_private():
                raise TypeError("Invalid private key provided")
            
            if not ciphertext:
                raise ValueError("Ciphertext cannot be empty")
            
            # Base64解码
            try:
                ciphertext_bytes = base64.b64decode(ciphertext)
            except Exception as e:
                raise ValueError("Invalid base64 encoded ciphertext") from e
            
            # 使用PKCS1_OAEP进行解密
            cipher = PKCS1_OAEP.new(pri_key)
            message = cipher.decrypt(ciphertext_bytes)
            
            return message
            
        except TypeError as e:
            logger.error(f"Type error during RSA decryption: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Value error during RSA decryption: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise