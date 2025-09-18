from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config.logs import logger
from settings import settings

# 数据库连接类

# 连接数据库
# SQLALCHEMY_DATABASE_URL = "sqlite:///.data.db"
SQLALCHEMY_DATABASE_URL = settings.database_url
# 创建一个数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=180,
    echo=True,
    pool_size=50,  # 调整池大小
    max_overflow=100  # 调整溢出量
)
logger.info("开始连接数据库...")
# 会话类，该类本身还不是数据库会话，实例化后每个实例将是一个数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建一个Base类
class Base(DeclarativeBase):
    pass

with engine.connect() as conn:
    if conn:
        logger.info("数据库连接成功")
    else:
        logger.error("数据库连接失败")


# 获取数据库连接
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
