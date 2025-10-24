import base64
import json
import logging
import mimetypes
import os.path
from datetime import datetime
from typing import Dict, Any, List

from sqlmodel import Session

from capsules.audit.repository.audits import audit_repository
from capsules.authorization.models.claim import CapsuleClaimModel
from capsules.authorization.models.collector import CollectorPropModel
from capsules.authorization.repository.capsule_claim import capsule_claim_repo
from capsules.authorization.services.capsule_privacy import capsule_privacy_srv
from capsules.core.models.additional_props import CapsuleAdditionalPropsModel
from capsules.core.models.capsule import DataCapsuleModel
from capsules.core.repository.additional_props import additional_props_repository
from capsules.core.repository.data_capsule import data_capsule_repo
from capsules.utils import minio_client
from capsules.utils.pdf_processor import PdfProcessor
from common.bus_exception import BusException
from common.db_deps import SessionDep
from llm.medical.capsule_loader import CapsuleLoader
from pki.kms import SecretKey, DigitalSignature
from pki.kms.core.aes import AESCipher
from pki.kms.core.rsa import RSACipher
from pki.kms.key_model import KeyModel
from pki.kms.key_repository import key_repository

logger = logging.getLogger(__name__)

class CapsuleService:
    def __init__(self):
        self.pdf_processor = PdfProcessor()

    async def wrap_data_capsule(self, db: SessionDep, file: str, props: CollectorPropModel) -> str | None:
        """
        根据传入的报告内容和附属信息，进行1阶胶囊的数据封装

        参数:
        - file： 医疗数据报告地址
        - props: 报告附属信息

        处理流程：
        - 预处理：
            - 判断输入文件类型：PDF | JPEG
            - 如果是PDF,通过pdf_processor工具类提取PDF文档完整内容，其输出结构为Markdown格式；
            - 如果是JPEG，则通过视觉理解模型提取图片内容；
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
        - 从KMS服务获取对称加密密钥，采用AES-CBC加密算法对raw_data, summary_data和gene_data进行加密；
        - 采用数据银行的私钥对数据内容进行签名得到signature；
        - 存储1阶胶囊数据到DBMS， 并存储数据加密密钥到secret_keys
        - 原始医疗影像数据的存储到MinIO对象存储
        - 生成数据采集者到数据拥有者的授权记录
        - 生成1阶胶囊封装审计日志
        """
        try:
            # 1. 预处理阶段
            # 1.1 检测输入文件是否存在
            logger.info("Processing medical report")
            if not os.path.exists(file):
                logger.error(f"File not found: {file}")
                raise BusException(code=10001, message="上传的医疗检测报告文件不存在。")

            # 1.2 获取文档的MIME类型,如果是图片类型，则通过调用视觉理解LLM进行处理，并返回处理结果
            mime_type = mimetypes.guess_type(file)[0]
            if mime_type and mime_type.startswith("image/"):
                logger.info("Processing image")
                source_data = await self._extract_raw_data_from_vision(file)
            else:
                logger.info("Processing PDF")
                source_data = PdfProcessor.extract_content_for_markdown(file, False, False)

            if not source_data:
                raise BusException(code=10002, message="解析用户医疗检测报告内容失败")
            
            # 1.2 将解析出来的内容交给LLM提取原始数据内容JSON
            raw_data = await self._extract_raw_data_from_llm(source_data)
            
            # 1.3 采用ZKP算法计算数据概要数据
            summary_data = await self._generate_summary_data(source_data)
            
            # 1.4 生成基因数据
            gene_data = await self._generate_gene_data(props)
            
            # 2. 加密阶段
            # 如果已经存在可用的AES密钥，则直接使用
            existed_aes_key = await self._get_aes_key(db)
            if not existed_aes_key:
                # 2.1 从KMS服务获取对称加密密钥
                logger.info("Generating AES key")
                aes_key = AESCipher.generate_key()
                aes_iv = AESCipher.generate_iv()
            else:
                # 2.2 从数据库中获取密钥,并将base64编码后的密钥和初始向量进行base64解码转为bytes类型
                logger.info("Use the exist AES key.")
                aes_key = base64.b64decode(existed_aes_key.aes_key)
                aes_iv = base64.b64decode(existed_aes_key.aes_iv)

            aes_cipher = AESCipher(aes_key, aes_iv)
            
            # 2.2 采用AES-CBC加密算法对raw_data, zkp_data和gene_data进行加密
            logger.info("Encrypting data")
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
                producer_time=props.collector_time,
                owner=props.owner,
                sexy=props.sexy,
                type=props.type,
                level=1
            )
            additional_props = await additional_props_repository.create_additional_props(db, additional_props_model)
            
            # 3.2 存储数据加密密钥到secret_keys (这里简化处理，实际应安全存储)

            secret_key = await self._store_encryption_key(db, aes_key, aes_iv) if not existed_aes_key else existed_aes_key
            # 3.3 创建数据胶囊
            data_capsule_model = DataCapsuleModel(
                summary_ciphertext=summary_encrypted,
                gene_ciphertext=gene_encrypted,
                raw_ciphertext=raw_encrypted,
                signature=signature,
                aes_key_id=secret_key.id,
                additional_props_id=additional_props.id
            )
            # 3.4 存储到数据库
            data_capsule = await data_capsule_repo.create_data_capsule(db, data_capsule_model)
            # 4. (可选)原始医疗影像数据的存储到MinIO对象存储
            await self._store_medical_images(file, data_capsule.uuid)
            logger.info(f"Data capsule created successfully with UUID: {data_capsule.uuid}")
            await self._generate_claim(db, data_capsule.uuid, props.owner, props.collector)
            await self._generate_audit_log(db, data_capsule.uuid)

            return data_capsule.uuid
            
        except Exception as e:
            logger.error(f"Failed to wrap data capsule: {str(e)}")
            raise BusException(code=10007, message="数据胶囊封装失败")

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
            raise BusException(code=10003, message="解析用户医疗检测报告提取BNF内容失败")

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
            raise BusException(code=10004, message="解析用户医疗检测报告生成数据概要失败")

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
            "collector_time": props.collector_time if props.collector_time else "未知时间",
            "customer": props.owner if props.owner else "未知客户",
            "gene_type": props.type if props.type else "未知报告类型",
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
            data_str = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else data
            data_bytes = data_str.encode('utf-8')
            
            # 使用AES加密
            encrypted_data = aes_cipher.encrypt(data_bytes)
            logger.info(f"Encrypted data: {encrypted_data}")
            return encrypted_data
        except Exception as e:
            logger.error(f"Failed to encrypt data: {str(e)}")
            raise BusException(code=10005, message="加密解析后的医疗数据失败")

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
            # TODO: 获取数据银行的数字证书
            private_key = "数字证书.pem"
            # 使用RSA私钥签名
            digital_signature = DigitalSignature()
            bytes_sig =  digital_signature.sign(data_to_sign, private_key)

            return base64.b64encode(bytes_sig).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to sign data: {str(e)}")
            raise BusException(code=10006, message="数据签名失败")

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
            key_model.aes_key = base64.b64encode(key).decode('utf-8')
            key_model.aes_iv = base64.b64encode(iv).decode('utf-8')
            # 存储1阶胶囊加密密钥
            secret_key= await key_repository.create_key(db, key_model)
            
            logger.info(f"Encryption key stored")
            return secret_key
        except Exception as e:
            logger.error(f"Failed to store encryption key: {str(e)}")
            raise BusException(code=10009, message="存储数据加密密钥失败")

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
            # 获取当前文件的Mine Type
            mine_type = mimetypes.guess_type(file_path)[0]
            # PDF文件的mine type为application/pdf
            if not mine_type:
                mine_type = "application/pdf"
            await minio_client.upload_file(file_path, capsule_uuid, mine_type)
            logger.info(f"Storing medical images to MinIO for capsule: {capsule_uuid}")
            return True
        except Exception as e:
            logger.error(f"Failed to store medical images: {str(e)}")
            raise BusException(code=10010, message="原始医疗影像数据存储失败")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def _get_aes_key(self, db):
        """
        从secret_key获取最新为废弃的密钥
        """
        return await key_repository.get_first_undeprecated_key(db)

    async def _generate_audit_log(self, db, uuid):
        """
        生成1阶胶囊封装日志记录
        """
        audit_log = await audit_repository.save_audit(db, {"capsule_uuid": uuid})
        logger.info(f"Audit log generated for capsule: {uuid}")
        return audit_log

    async def get_raw_data(self, db: SessionDep, uuid: str) -> str:
        """
        获取原始数据

        Args:
            db: 数据库会话
            uuid: 胶囊UUID

        Returns:
            str: 原始数据
        """
        # 根据胶囊的uuid从MinIO对象存储获取原始数据的签名访问链接
        return minio_client.get_file_url(uuid)

    async def list_capsules(self, db: SessionDep, offset: int = 0, limit: int = 10) -> List[DataCapsuleModel]:
        """
        列出1阶胶囊列表

        Args:
            db: 数据库会话
            offset: 偏移量
            limit: 限制数量

        Returns:
            List[DataCapsuleModel]: 1阶胶囊列表
        """
        return await data_capsule_repo.list_data_capsule(db, offset, limit)

    async def list_capsules_by_owner(self, db: SessionDep, owner: str, offset: int = 0, limit: int = 10) -> List[DataCapsuleModel]:
        """
        列出指定用户创建的1阶胶囊列表

        Args:
            db: 数据库会话
            owner: 胶囊拥有者
            offset: 偏移量
            limit: 限制数量

        Returns:
            List[DataCapsuleModel]: 1阶胶囊列表
        """
        return await data_capsule_repo.list_data_capsules_by_owner(db, owner, offset, limit)

    async def grant_capsules(self, db: SessionDep, claim: CapsuleClaimModel, signature: str) -> str:
        """
        授权1阶胶囊给其他用户

        Args:
            db: 数据库会话
            claim: 授权信息

        Returns:
            str: 授权结果, 授权包唯一标识UUID
        """
        # TODO: 验证授权者数字证书签名

        capsule_claim = await capsule_claim_repo.create_capsule_claim(db, claim,  signature)
        if not capsule_claim:
            raise BusException(20001, "授权失败")
        return capsule_claim.uuid

    async def get_capsules_by_claim(self, db, claim_uuid, owner):
        """
        根据授权指令获取1阶胶囊数据信息
        """
        # 验证授权指令
        logger.info(f"Get capsules by claim: {claim_uuid}")
        if not claim_uuid:
            logger.error("Claim UUID cannot be empty")
            raise BusException(20002, "授权指令不能为空")
        claim = await capsule_claim_repo.get_capsule_claim(db, claim_uuid)
        if owner != claim.receiver:
            logger.error("Data access applicant and authorization instruction owner information do not match")
            raise BusException(20003, "数据访问申请者和授权指令拥有者信息不匹配")
        # 验证授权指令是否过期
        if claim.expires_at < datetime.now():
            logger.error("Authorization instruction has expired")
            raise BusException(20004, "授权指令已过期")
        # 如果授权指令的隐私级级为公开，则返回数据信息
        if claim.privacy_level == 0:
            logger.info("Public authorization instruction")
            capsules = await data_capsule_repo.list_capsules_by_uuids(db, claim.capsules)
            if claim.one_time_use:
                await capsule_claim_repo.deprecate_capsule_claim(db, claim_uuid)
            return capsules
        # 非公开授权指令，则调用权益管理模块返回计算后的数据信息
        return await capsule_privacy_srv.get_capsules_by_claim(claim)

    async def _generate_claim(self, db, uuid, owner, collector):
        pass

    async def _extract_raw_data_from_vision(self, file):
        """
        调用视觉理解模型解析图片内容
        """
        # 1. 将图片内容读取并转为Base64编码
        with open(file, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        # 2. 调用视觉理解模型解析图片内容
        try:
            capsule_loader = CapsuleLoader()
            return await capsule_loader.extract_text_from_image(image_base64)
        except Exception as e:
            logger.error(f"Failed to extract text from image: {str(e)}")
            raise BusException(10008, "图片内容解析失败")



capsule_srv = CapsuleService()