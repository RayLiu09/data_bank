# -*- coding: utf-8 -*-
import base64
import logging

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger(__name__)

class AESCipher:
    def __init__(self, key: bytes, iv: bytes = None):
        """
        AESCipher类初始化函数

        基于AES.new创建对象实例，需要指定nonce和mode of operation
        Args:
            key: AES密钥， 可以是128字节长度AES-128， 192字节长度AES-192, 256字节长度AEC-256
            iv: IV, Initialization Vector
            mode: AES.MODE_GCM | AES.MODE_CBC
        """
        self.key = key
        self.block_size = 16
        self.mode = AES.MODE_CBC
        if iv is None:
            self.iv = get_random_bytes(self.block_size)
        else:
            self.iv = iv

        self.cipher = AES.new(self.key, self.mode, self.iv)

    @staticmethod
    def generate_key() -> bytes:
        """
        生成32字节的AES加密密钥，用于AES-256加密算法

        Returns:
            bytes: 32字节的随机密钥
        """
        return get_random_bytes(32)

    @staticmethod
    def generate_iv() -> bytes:
        """
        生成16字节的CBC模式IV值

        Returns:
            bytes: 16字节的随机IV值
        """
        return get_random_bytes(16)

    def encrypt(self, message: bytes) -> str:
        """
        对消息进行加密（CBC模式）

        Args:
            message: 待加密的消息内容

        Returns:
            str: 加密后的消息内容base64格式
        """
        try:
            if not isinstance(message, bytes):
                raise TypeError("Message must be bytes")
            
            if not message:
                raise ValueError("Message cannot be empty")
            
            # 对消息进行填充以匹配块大小
            padded_message = pad(message, self.block_size)
            
            # 创建新的加密器实例以避免重复使用nonce
            cipher = AES.new(self.key, self.mode, self.iv)
            
            # 加密数据
            ciphertext = cipher.encrypt(padded_message)
            
            # 将加密结果转换为base64编码的字符串
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt(self, ciphertext: str) -> bytes:
        """
        对消息进行解密（CBC模式）

        Args:
            ciphertext: 待解密的消息内容(base64编码的字符串)

        Returns:
            bytes: 解密后的消息内容
        """
        try:
            if not isinstance(ciphertext, str):
                raise TypeError("Ciphertext must be a base64 encoded string")
            
            if not ciphertext:
                raise ValueError("Ciphertext cannot be empty")
            
            # 将base64编码的字符串解码为bytes
            ciphertext_bytes = base64.b64decode(ciphertext)
            
            # 检查密文长度是否为块大小的整数倍
            if len(ciphertext_bytes) % self.block_size != 0:
                raise ValueError("Invalid ciphertext length")
            
            # 创建新的解密器实例
            cipher = AES.new(self.key, self.mode, self.iv)
            padded_message = cipher.decrypt(ciphertext_bytes)
            
            # 去除填充
            message = unpad(padded_message, self.block_size)
            
            return message
        except ValueError as e:
            logger.error(f"Decryption failed due to padding error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def encrypt_ocb(self, message: bytes) -> str:
        """
        使用OCB模式对消息进行加密

        Args:
            message: 待加密的消息内容

        Returns:
            str: 加密后的消息内容base64格式（包含密文和认证标签）
        """
        try:
            if not isinstance(message, bytes):
                raise TypeError("Message must be bytes")
            
            if not message:
                raise ValueError("Message cannot be empty")
            
            # 生成随机nonce用于OCB模式
            nonce = get_random_bytes(15)  # OCB模式推荐的nonce长度
            
            # 创建OCB模式的加密器
            cipher = AES.new(self.key, AES.MODE_OCB, nonce=nonce)
            
            # 加密数据
            ciphertext, auth_tag = cipher.encrypt_and_digest(message)
            
            # 将nonce、密文和认证标签组合后进行base64编码
            result = nonce + ciphertext + auth_tag
            return base64.b64encode(result).decode('utf-8')
            
        except Exception as e:
            logger.error(f"OCB encryption failed: {str(e)}")
            raise

    def decrypt_ocb(self, encrypted_data: str) -> bytes:
        """
        使用OCB模式对消息进行解密

        Args:
            encrypted_data: 待解密的消息内容(base64编码的字符串，包含nonce、密文和认证标签)

        Returns:
            bytes: 解密后的消息内容
        """
        try:
            if not isinstance(encrypted_data, str):
                raise TypeError("Encrypted data must be a base64 encoded string")
            
            if not encrypted_data:
                raise ValueError("Encrypted data cannot be empty")
            
            # base64解码
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # 检查数据长度
            if len(encrypted_bytes) < 15 + 16:  # nonce(15) + tag(16)的最小长度
                raise ValueError("Invalid encrypted data length")
            
            # 提取nonce、密文和认证标签
            nonce = encrypted_bytes[:15]
            auth_tag = encrypted_bytes[-16:]  # OCB模式的认证标签长度为16字节
            ciphertext = encrypted_bytes[15:-16]
            
            # 创建OCB模式的解密器
            cipher = AES.new(self.key, AES.MODE_OCB, nonce=nonce)
            
            # 解密数据
            message = cipher.decrypt_and_verify(ciphertext, auth_tag)
            
            return message
            
        except ValueError as e:
            logger.error(f"OCB decryption failed due to verification error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"OCB decryption failed: {str(e)}")
            raise