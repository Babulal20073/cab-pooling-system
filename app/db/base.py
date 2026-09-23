#setup databases with using sqlalchemy orm
#original inherited class for every model
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass