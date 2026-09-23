from sqlalchemy import String,Enum as SAEnum
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
from app.models.enums import Role,Gender

class Employee(Base):
    __tablename__="employees"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(100))
    email:Mapped[str] = mapped_column(String(150),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    gender:Mapped[Gender]=mapped_column(SAEnum(Gender))
    role:Mapped[Role]=mapped_column(SAEnum(Role),default=Role.EMPLOYEE)
    home_lat:Mapped[float]
    home_lng:Mapped[float]

    bookings:Mapped[list["Booking"]] = relationship(back_populates="employee")
    stops:Mapped[list["Stop"]]=relationship(back_populates="employee")
