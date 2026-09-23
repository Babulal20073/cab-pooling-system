from sqlalchemy import ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Cab(Base):
    __tablename__="cabs"
    id:Mapped[int] = mapped_column(primary_key=True)
    shift_id:Mapped[int]=mapped_column(ForeignKey("shifts.id"))
    capacity:Mapped[int]
    guard_assigned:Mapped[bool]=mapped_column(Boolean,default=False)

    shift:Mapped["Shift"]=relationship(back_populates="cabs")
    stops:Mapped[list["Stop"]]=relationship(back_populates="cab",order_by="Stop.sequence_no")
    