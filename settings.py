#
# FastApi系统配置文件
# 运行前：请修改此配置文件cli方式启动
#
import os

from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    # 系统名称
    project_name: str = "数据银行平台"
    # API版本号
    api_version: str = "v1"
    # 语言
    locale: str = "zh"
    # 服务器配置
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    # Host配置
    trusted_hosts: list[str] = ["*"]
    # Mysql配置从环境变量中获取
    database_url: str = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4&autocommit=true".format(
        os.environ.get("DATABASE_USER", "mysql"),
        os.environ.get("DATABASE_PASSWORD", "MySQL_2024"),
        os.environ.get("DATABASE_HOST", "192.168.1.182"),
        os.environ.get("DATABASE_PORT", "3306"),
        os.environ.get("DATABASE_NAME", "data_bank"),
    )

    # Minio本地存储配置
    minio_url: str = os.environ.get("MINIO_URL", "192.168.1.182")
    minio_port: int = 9000
    minio_access_key: str = os.environ.get("MINIO_ACCESS_KEY", "minio")
    minio_secret_key: str = os.environ.get("MINIO_SECRET_KEY", "minio123")
    minio_bucket: str = os.environ.get("MINIO_BUCKET", "data-bank")
    # Weaviate
    weaviate_host: str = os.environ.get("WEAVIATE_HOST", "192.168.1.182")
    weaviate_port: int = os.environ.get("WEAVIATE_PORT", "8080")
    weaviate_grpc_port: int = 50051
    # Chunking
    chunk_size: int = 1024
    chunk_overlap: int = 20
    chunk_type: str = "word"
    default_openai_embedding_model: str = "text-embedding-ada-002"
    # JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 12
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # openAI代理地址
    openai_api_base: str = os.environ.get("OPENAI_API_BASE", "")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")

    openai_tti_base: str = os.environ.get("OPENAI_TTI_BASE", "")
    openai_tti_key: str = os.environ.get("OPENAI_TTI_KEY", "")
    # 通义千问
    qwen_api_base: str = os.environ.get("QWEN_API_BASE", "")
    qwen_api_key: str = os.environ.get("QWEN_API_KEY", "")
    # 火山引擎
    vol_api_base: str = os.environ.get("VOL_API_BASE", "")
    vol_api_key: str = os.environ.get("VOL_API_KEY", "")
    vol_model_endpoint: str = os.environ.get("VOL_MODEL_ENDPOINT", "")

    # 默认模型
    sel_model_provider: str = os.environ.get("SEL_MODEL_PROVIDER", "openai")

    # 密钥保护密码
    SECRET_PASSPHRASE: str = os.environ.get("SECRET_PASSPHRASE", "")
    # 日志设置
    log_level: str = "waring"
    log_dir: str = "./logs"
    # 临时文件目录
    tmp_dir: str = "./upload"
    # 密钥目录
    certs_dir: str = "./certs"

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s %(asctime)s %(name)s %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "WARNING",
            },
        },
        "loggers": {
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建配置对象
settings = APISettings()
