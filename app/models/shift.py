#for specific timing of a shift
#Use enum safety validator for day or night shift 
#For fixed contraint with safety issue

from datetime import datetime
from sqlalchemy import ForeignKey,Enum as SAEnum
from sqlalchemy.orm import Mapped , mapped_column, relationship
from app.db.base import Base
from app.models.enums import ShiftType

class Shift(Base):
    __tablename__="shifts"

    id:Mapped[int] = mapped_column(primary_key=True)
    office_id:Mapped[int]=mapped_column(ForeignKey("offices.id"))
    start_time:Mapped[datetime]
    shift_type:Mapped[ShiftType]=mapped_column(SAEnum(ShiftType))

    office:Mapped["Office"]=relationship(back_populates="shifts")
    bookings:Mapped[list["Booking"]]=relationship(back_populates="shift")
    cabs:Mapped[list["Cab"]] = relationship(back_populates="shift")
