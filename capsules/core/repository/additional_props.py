from sqlmodel import Session

from capsules.core.models.additional_props import CapsuleAdditionalPropsModel
from capsules.core.schema import CapsuleAdditionalProps


class CapsuleAdditionalPropsRepository:
    def __init__(self):
        pass

    async def create_additional_props(self, db: Session, additional_props_in: CapsuleAdditionalPropsModel) -> CapsuleAdditionalProps:
        """
        Create a capsule additional props
        :param db:
        :param additional_props_in:
        :return:
        """
        additional_props = CapsuleAdditionalProps(
            owner=additional_props_in.owner,
            sexy=additional_props_in.sexy,
            age=additional_props_in.age,
            area=additional_props_in.area,
            type=additional_props_in.type,
            producer=additional_props_in.producer
        )
        db.add(additional_props)
        db.commit()
        db.refresh(additional_props)
        return additional_props

additional_props_repository = CapsuleAdditionalPropsRepository()