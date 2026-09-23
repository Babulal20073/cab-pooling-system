from sqlalchemy.orm import Session

from app.models.office import Office
from app.schemas.office import OfficeCreate
from app.exceptions import OfficeAlreadyExistsError
from app.exceptions import OfficeAlreadyExistsError
from sqlalchemy.orm import Session

from app.models.office import Office
from app.schemas.office import OfficeCreate


class OfficeService:

    def __init__(self, db: Session):
        self.db = db

    def create_office(self, data: OfficeCreate) -> Office:

        existing_office = (
            self.db.query(Office)
            .filter(Office.name == data.name)
            .first()
        )

        if existing_office:
            raise OfficeAlreadyExistsError(
                "Office already exists"
            )

        office = Office(
            name=data.name,
            lat=data.lat,
            lng=data.lng,
        )

        self.db.add(office)
        self.db.commit()
        self.db.refresh(office)

        return office