import json
import logging
import os.path
import uuid
from datetime import datetime
from typing import Dict, Any

from sqlmodel import Session

from capsules.authorization.models.collector import CollectorPropModel
from capsules.core.models.additional_props import CapsuleAdditionalPropsModel
from capsules.core.models.capsule import DataCapsuleModel
from capsules.core.repository.additional_props import additional_props_repository
from capsules.core.repository.data_capsule import data_capsule_repo
from capsules.utils import minio_client
from capsules.utils.pdf_processor import PdfProcessor
from llm.medical.capsule_loader import CapsuleLoader
from pki.kms import SecretKey
from pki.kms.core.aes import AESCipher
from pki.kms.core.rsa import RSACipher
from pki.kms.key_model import KeyModel
from pki.kms.key_repository import key_repository

logger = logging.getLogger(__name__)

class CapsuleService:
    def __init__(self):
        self.pdf_processor = PdfProcessor()

    async def wrap_data_capsule(self, db: Session, file: str, props: CollectorPropModel) -> str | None:
        """
        根据传入的报告内容和附属信息，进行1阶胶囊的数据封装

        参数:
        - file： 医疗数据报告地址
        - props: 报告附属信息

        处理流程：
        - 预处理：
            - 通过pdf_processor工具类提取PDF文档完整内容，其输出结构为Markdown格式；
            - 将上一步解析出来的内容交给LLM，根据定义好的BNF数据规范提取出原始数据内容JSON， 定义为raw_data
            - 计算数据概要数据， 定义为summary_data
            - 生成基因数据， 如{"collector_agent": "xxx三甲医院检测中心",
                "collector_time": "2021-01-01 00:00:00",
                "customer": "张三",
                "gene_type": "基因检测",
                # 开方医生
                "open_doctor": "李医生",
                # 检测执行人员
                "executor": "王医生",
                # 科室名称
                "department": " Bioinformatics"}，定义为gene_data
        - 从KMS服务获取对称加密密钥，采用AES-GCM加密算法对raw_data, summary_data和gene_data进行加密， 同时采用数据银行的私钥对数据内容进行签名得到signature
        - 存储1阶胶囊数据到DBMS， 并存储数据加密密钥到secret_keys
        - (可选)原始医疗影像数据的存储到MinIO对象存储
        """
        try:
            # 1. 预处理阶段
            # 1.1 通过pdf_processor工具类提取PDF文档完整内容
            logger.info("Processing medical report")
            if not os.path.exists(file):
                logger.error(f"File not found: {file}")
                return None

            markdown_content = PdfProcessor.extract_content_for_markdown(file, False, False)
            if not markdown_content:
                raise ValueError("Failed to process PDF file")
            
            # 1.2 将解析出来的内容交给LLM提取原始数据内容JSON
            raw_data = await self._extract_raw_data_from_llm(markdown_content)
            
            # 1.3 采用ZKP算法计算数据概要数据
            summary_data = await self._generate_summary_data(markdown_content)
            
            # 1.4 生成基因数据
            gene_data = await self._generate_gene_data(props)
            
            # 2. 加密阶段
            # 如果已经存在可用的AES密钥，则直接使用
            existed_aes_key = await self._get_aes_key(db)
            if not existed_aes_key:
                # 2.1 从KMS服务获取对称加密密钥
                aes_key = AESCipher.generate_key()
                aes_iv = AESCipher.generate_iv()
            else:
                aes_key = existed_aes_key.aes_key
                aes_iv = existed_aes_key.aes_iv
            aes_cipher = AESCipher(aes_key, aes_iv)
            
            # 2.2 采用AES-CBC加密算法对raw_data, zkp_data和gene_data进行加密
            raw_encrypted = self._encrypt_data(raw_data, aes_cipher)
            summary_encrypted = self._encrypt_data(summary_data, aes_cipher)
            gene_encrypted = self._encrypt_data(gene_data, aes_cipher)
            
            # 2.3 采用数据银行的私钥对数据内容进行签名得到signature
            signature = self._sign_data(raw_data, summary_data, gene_data)
            logger.info(f"Signing data: {signature}")
            # 3. 存储阶段

            # 3.1 创建胶囊附属信息
            additional_props_model = CapsuleAdditionalPropsModel(
                age=props.age,
                area=props.area,
                producer=props.collector,
                producer_time=datetime.now(),# 获取当前时间， 后续需要从医疗报告中获取报告产生时间
                owner=props.owner,
                sexy=props.sexy,
                type=props.type,
                level=1
            )
            additional_props = await additional_props_repository.create_additional_props(db, additional_props_model)
            
            # 3.2 存储数据加密密钥到secret_keys (这里简化处理，实际应安全存储)
            if not existed_aes_key:
                secret_key = await self._store_encryption_key(db, aes_key, aes_iv)
            # 3.3 创建数据胶囊
            data_capsule_model = DataCapsuleModel(
                summary_ciphertext=summary_encrypted,
                gene_ciphertext=gene_encrypted,
                raw_ciphertext=raw_encrypted,
                signature=signature,
                aes_key_id=secret_key.id if not existed_aes_key else existed_aes_key.id,
                additional_props_id=additional_props.id
            )
            # 3.4 存储到数据库
            data_capsule = await data_capsule_repo.create_data_capsule(db, data_capsule_model)
            # 4. (可选)原始医疗影像数据的存储到MinIO对象存储
            await self._store_medical_images(file, data_capsule.uuid)
            
            logger.info(f"Data capsule created successfully with UUID: {data_capsule.uuid}")
            return data_capsule.uuid
            
        except Exception as e:
            logger.error(f"Failed to wrap data capsule: {str(e)}")
            raise

    async def _extract_raw_data_from_llm(self, markdown_content: str) -> Dict[str, Any]:
        """
        将解析出来的内容交给LLM，根据定义好的BNF数据规范提取出原始数据内容JSON
        
        Args:
            markdown_content: PDF解析后的Markdown内容
            
        Returns:
            Dict[str, Any]: 原始数据内容JSON
        """
        # 实现与LLM的交互，将markdown_content交给LLM处理
        # 后续代码需要写入到llm包的medical子包下对应的代码文件里面
        logger.info("Extracting raw data from LLM")
        # 临时返回示例数据
        try:
            capsule_loader = CapsuleLoader()
            return await capsule_loader.calc_raw_data_by_bnf(markdown_content)
        except Exception as e:
            logger.error(f"Failed to extract raw data: {str(e)}")
            raise

    async def _generate_summary_data(self, raw_data: str) -> str:
        """
        将raw_data将给LLM生成原始数据的精简概要数据
        
        Args:
            raw_data: 原始数据
            
        Returns:
            str: 数据概要
        """
        # 实现数据概要计算逻辑
        logger.info("Generating summary data - placeholder implementation")
        # raw_data = json.dumps(raw_data, ensure_ascii=False)
        # 临时返回示例数据
        try:
            capsule_loader = CapsuleLoader()
            return await capsule_loader.calc_summary_data_by_bnf(raw_data)
        except Exception as e:
            logger.error(f"Failed to generate ZKP data: {str(e)}")
            raise

    async def _generate_gene_data(self, props: CollectorPropModel) -> Dict[str, Any]:
        """
        生成基因数据
        
        Args:
            props: 报告附属信息
            
        Returns:
            Dict[str, Any]: 基因数据
        """
        gene_data = {
            "collector_agent": props.collector if props.collector else "未知检测机构",
            "collector_time": datetime.now().isoformat(), # TODO: 后续根据报告时间获取
            "customer": props.owner if props.owner else "未知客户",
            "gene_type": props.type if props.type else "基因检测",
            "open_doctor": "未知医生", # TODO: 后续根据报告获取执行医生
            "executor": "未知执行人", # TODO: 后续根据报告获取执行医生
            "department":  "未知科室", # TODO: 后续根据报告获取执行医生
            "level": 1,
            "age": props.age if props.age else 0,
            "area": props.area if props.area else "未知地区",
            "sexy": props.sexy if props.sexy else 0,
        }
        
        return gene_data

    def _encrypt_data(self, data: str | Dict[str, Any], aes_cipher: AESCipher) -> str:
        """
        使用AES-GCM加密算法对数据进行加密
        
        Args:
            data: 待加密的数据
            aes_cipher: 加密密钥
            
        Returns:
            str: 加密后的数据(base64编码)
        """
        try:
            # 将数据转换为JSON字符串
            data_str = json.dumps(data, ensure_ascii=False)
            data_bytes = data_str.encode('utf-8')
            
            # 使用AES加密
            encrypted_data = aes_cipher.encrypt(data_bytes)
            
            return encrypted_data
        except Exception as e:
            logger.error(f"Failed to encrypt data: {str(e)}")
            raise

    def _sign_data(self, raw_data: Dict[str, Any], summary_data: str | Dict[str, Any], gene_data: Dict[str, Any]) -> str:
        """
        采用数据银行的私钥对数据内容进行签名
        
        Args:
            raw_data: 原始数据
            summary_data: ZKP数据
            gene_data: 基因数据
            
        Returns:
            str: 签名结果
        """
        try:
            # 将数据组合成待签名字符串
            data_to_sign = json.dumps({
                "raw_data": raw_data,
                "summary_data": summary_data,
                "gene_data": gene_data
            }, sort_keys=True)
            
            # 使用RSA私钥签名
            rsa_cipher = RSACipher()
            signature = rsa_cipher.digital_sign(data_to_sign)
            
            return signature
        except Exception as e:
            logger.error(f"Failed to sign data: {str(e)}")
            raise

    async def _store_encryption_key(self, db: Session, key: bytes, iv: bytes) -> SecretKey:
        """
        存储数据加密密钥到secret_keys
        
        Args:
            db: 数据库会话
            capsule_uuid: 胶囊UUID
            key: 加密密钥
            signature: 数据签名
            
        Returns:
            bool: 是否存储成功
        """
        try:
            # 创建附加属性记录来存储密钥信息
            key_model = KeyModel()
            key_model.aes_key = key.hex()
            key_model.aes_iv = iv.hex()
            # 存储1阶胶囊加密密钥
            secret_key= await key_repository.create_key(db, key_model)
            
            logger.info(f"Encryption key stored")
            return secret_key
        except Exception as e:
            logger.error(f"Failed to store encryption key: {str(e)}")
            raise

    async def _store_medical_images(self, file_path: str, capsule_uuid: str) -> bool:
        """
        (可选)原始医疗影像数据的存储到MinIO对象存储
        
        Args:
            file_path: 文件路径
            capsule_uuid: 胶囊UUID
            
        Returns:
            bool: 是否存储成功
        """
        try:
            # 实现医疗影像数据存储到MinIO
            await minio_client.upload_file(file_path, capsule_uuid)
            logger.info(f"Storing medical images to MinIO for capsule: {capsule_uuid}")
            return True
        except Exception as e:
            logger.error(f"Failed to store medical images: {str(e)}")
            raise
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def _get_aes_key(self, db):
        """
        从secret_key获取最新为废弃的密钥
        """
        return await key_repository.get_first_undeprecated_key(db)


capsule_srv = CapsuleService()