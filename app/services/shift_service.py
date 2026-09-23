from sqlalchemy.orm import Session

from app.schemas.shift import ShiftCreate
from app.exceptions import OfficeNotFoundError
from app.models.shift import Shift
from app.models.office import Office

class ShiftService:
    def __init__(self,db:Session):
        self.db=db

    def create_shift(self,data:ShiftCreate)->Shift:
        office=(
            self.db.query(Office)
            .filter(Office.id==data.office_id)
            .first()
        )
        if not office:
            raise OfficeNotFoundError(
                "Office not found"
            )

        shift = Shift(
            office_id=data.office_id,
            start_time=data.start_time,
            shift_type=data.shift_type,
        )

        self.db.add(shift)
        self.db.commit()
        self.db.refresh(shift)

        return shift