#it's just a named keypoint
#Kept separate from Shifts
#becuase one office runs many shifts
#and it's coordinates and fiexed for every cab
from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base

class Office(Base):
    __tablename__="offices"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True)
    lat:Mapped[float]
    lng:Mapped[float]

    shifts:Mapped[list["Shift"]] = relationship(back_populates="office")