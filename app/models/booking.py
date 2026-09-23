#SO here we will do two things 
#setup booking it will require id(unique),shift,office,employee and booking_status
#Set uniqueConstraint so that we can check for duplicacy here rather then
#putting if condition

from datetime import datetime,timezone
from sqlalchemy import ForeignKey,UniqueConstraint,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
from app.models.enums import BookingStatus

class Booking(Base):
    __tablename__="bookings"
    __table_args__ = (UniqueConstraint("employee_id","shift_id",name="uq_employee_shift"),)

    id:Mapped[int]=mapped_column(primary_key=True)
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    shift_id:Mapped[int]=mapped_column(ForeignKey("shifts.id"))
    status:Mapped[BookingStatus]=mapped_column(SAEnum(BookingStatus),default=BookingStatus.ACTIVE)
    created_at: Mapped[datetime]=mapped_column(default=lambda:datetime.now(timezone.utc))

    employee:Mapped["Employee"]=relationship(back_populates="bookings")
    shift:Mapped["Shift"]=relationship(back_populates="bookings")