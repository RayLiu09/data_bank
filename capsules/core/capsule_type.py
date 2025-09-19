from enum import Enum

class CapsuleType(str, Enum):
    """
    CapsuleType is an enum that represents the different types of capsules.
    """
    # 影像学检查报告类型
    CT = "10001"  # CT影像报告
    DX = "10002"  # DX影像报告 (数字化X线摄影)
    MRI = "10003"  # MRI影像报告
    CR = "10004"  # CR影像报告 (计算机X线摄影)
    DR = "10005"  # DR影像报告 (数字化X线摄影)
    US = "10006"  # 超声检查报告
    PET = "10007"  # PET影像报告 (正电子发射断层扫描)
    PET_CT = "10008"  # PET-CT影像报告
    ECG = "10009"  # 心电图检查报告
    EEG = "10010"  # 脑电图检查报告
    EMG = "10011"  # 肌电图检查报告
    ECHO = "10012"  # 超声心动图检查报告
    MAMMOGRAPHY = "10013"  # 乳腺X线摄影报告
    DSA = "10014"  # 数字减影血管造影报告
    CTA = "10015"  # CT血管造影报告
    MRA = "10016"  # 磁共振血管造影报告

    # 实验室检查报告类型
    BLOOD_TEST = "20001"  # 血液检查报告
    URINE_TEST = "20002"  # 尿液检查报告
    STOOL_TEST = "20003"  # 粪便检查报告
    BIOCHEMISTRY = "20004"  # 生化检查报告
    IMMUNOLOGY = "20005"  # 免疫学检查报告
    HORMONE = "20006"  # 激素检查报告
    TUMOR_MARKER = "20007"  # 肿瘤标志物检查报告
    BLOOD_GAS = "20008"  # 血气分析报告
    COAGULATION = "20009"  # 凝血功能检查报告
    HEPATIC = "20010"  # 肝功能检查报告
    RENAL = "20011"  # 肾功能检查报告
    LIPID = "20012"  # 血脂检查报告
    GLUCOSE = "20013"  # 血糖检查报告
    CARDIAC_MARKER = "20014"  # 心肌标志物检查报告
    THYROID = "20015"  # 甲状腺功能检查报告
    MICROBIOLOGY = "20016"  # 微生物学检查报告
    PARASITOLOGY = "20017"  # 寄生虫学检查报告
    BLOOD_TYPING = "20018"  # 血型鉴定报告

    # 病理学检查报告类型
    PATHOLOGY = "30001"  # 病理检查报告
    CYTOLOGY = "30002"  # 细胞学检查报告
    HISTOLOGY = "30003"  # 组织学检查报告
    FROZEN_SECTION = "30004"  # 冰冻切片检查报告
    IMMUNOHISTOCHEMISTRY = "30005"  # 免疫组织化学检查报告
    MOLECULAR_PATHOLOGY = "30006"  # 分子病理学检查报告

    # 内窥镜检查报告类型
    GASTROSCOPY = "40001"  # 胃镜检查报告
    COLONOSCOPY = "40002"  # 肠镜检查报告
    BRONCHOSCOPY = "40003"  # 支气管镜检查报告
    LAPAROSCOPY = "40004"  # 腹腔镜检查报告
    CYSTOSCOPY = "40005"  # 膀胱镜检查报告
    LARYNGOSCOPY = "40006"  # 喉镜检查报告
    ARTHROSCOPY = "40007"  # 关节镜检查报告

    # 功能检查报告类型
    PULMONARY = "50001"  # 肺功能检查报告
    CARDIAC_STRESS = "50002"  # 心脏负荷试验报告
    HEARING_TEST = "50003"  # 听力检查报告
    VISION_TEST = "50004"  # 视力检查报告
    BONE_DENSITY = "50005"  # 骨密度检查报告
    SLEEP_STUDY = "50006"  # 睡眠监测报告
    EXERCISE_TEST = "50007"  # 运动负荷试验报告

    # 其他检查报告类型
    PHYSICAL_EXAM = "60001"  # 体格检查报告
    GENETIC_TEST = "60002"  # 基因检测报告
    ALLERGY_TEST = "60003"  # 过敏原检测报告
    DRUG_TEST = "60004"  # 药物检测报告
    VACCINATION = "60005"  # 疫苗接种记录报告
