from sqlmodel import Session

from capsules.authorization.models.collector import CollectorPropModel


class CapsuleService:
    def __init__(self):
        pass

    async def wrap_data_capsule(self, db: Session, file: str, props: CollectorPropModel) -> str:
        """
        根据传入的报告内容和附属信息，进行1阶胶囊的数据封装

        参数:
        - file： 医疗数据报告地址
        - props: 报告附属信息

        处理流程：
        - 预处理：
            - 通过将文件交给LLM，根据定义好的BNF数据规范提取出原始数据内容JSON， 定义为raw_data
            - 采用ZKP算法计算数据概要数据， 定义为zkp_data
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
        - 从KMS服务获取对称加密密钥，采用AES-GCM加密算法对raw_data, zkp_data和gene_data进行加密， 同时采用HMAC数据摘要算法计算raw_data, zkp_data和gene_data
            的数据摘要，分别保存为raw_digest, zkp_digest和gene_digest
        - 存储1阶胶囊数据到DBMS， 并存储数据加密密钥到secret_keys
        - (可选)原始医疗影像数据的存储
        """
