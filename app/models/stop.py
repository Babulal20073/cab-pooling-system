#It's for routing one pickup at one position in one cab's seqence
#sequence_no is the pickup order that we will set up by running algos
#eta is to show time taken for a perticular pickups
#This is also the table which we will modified to change or deleted service
#So it will be used for replanService

from datetime import datetime
from sqlalchemy import ForeignKey,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Stop(Base):
    __tablename__="stops"
    id:Mapped[int]=mapped_column(primary_key=True)
    cab_id:Mapped[int]=mapped_column(ForeignKey("cabs.id"))
    employee_id:Mapped[int]=mapped_column(ForeignKey("employees.id"))
    sequence_no:Mapped[int]
    eta:Mapped[datetime]
    is_pickup:Mapped[bool]=mapped_column(Boolean,default=True)

    cab:Mapped["Cab"]=relationship(back_populates="stops")
    employee:Mapped["Employee"]=relationship(back_populates="stops")
    