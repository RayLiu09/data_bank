from sqlmodel import Session, and_

from capsules.core.models.additional_props import CapsuleAdditionalPropsModel
from capsules.core.models.capsule import DataCapsuleModel
from capsules.core.schema import DataCapsule, CapsuleAdditionalProps


class DataCapsuleRepository:
    def __init__(self):
        pass

    async def create_data_capsule(self, db: Session, data_capsule_in: DataCapsuleModel) -> DataCapsule:
        """
        存储封装好的1阶胶囊到数据库
        """
        db_data_capsule = DataCapsule(**data_capsule_in.model_dump(exclude_unset= True))
        db.add(db_data_capsule)
        db.commit()
        db.refresh(db_data_capsule)
        return db_data_capsule

    async def get_data_capsule(self, db: Session, uuid: str) -> DataCapsule:
        """
        根据 capsule uuid 获取 capsule
        """
        db_data_capsule = db.query(DataCapsule).filter(DataCapsule.uuid == uuid).first()
        return db_data_capsule

    async def list_data_capsule(self, db: Session, skip: int = 0, limit: int = 1000) -> list[DataCapsule]:
        """
        获取所有 capsule
        """
        db_data_capsules = db.query(DataCapsule).offset(skip).limit(limit).all()
        return db_data_capsules

    async def get_data_capsule_by_additional_props(self, db: Session, additional_props_in: CapsuleAdditionalPropsModel) -> list[DataCapsule]:
        """
        根据附属信息查找符合条件的1阶数据胶囊
        """
        query = db.query(DataCapsule).join(CapsuleAdditionalProps, DataCapsule.additional_props_id == CapsuleAdditionalProps.id)
        # 添加查询条件
        conditions = []
        for key, value in additional_props_in.model_dump(exclude_unset=True, exclude={"area"}).items():
            conditions.append(getattr(CapsuleAdditionalProps, key) == value)
        # 添加地区查询条件
        if additional_props_in.area:
            pass

        if conditions:
            query = query.filter(and_(*conditions))

        return query.all()

data_capsule_repo = DataCapsuleRepository()