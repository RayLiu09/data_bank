try:
    from sqlalchemy.orm import DeclarativeBase
    class DBBase(DeclarativeBase):
        pass
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    DBBase = declarative_base()