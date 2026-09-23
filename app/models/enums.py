#creating enum values for variable category for provided options
#Can do validation of diffeent category under one Type 
#Such as Gender: "male","female","other"

import enum

class Role(str,enum.Enum):
    EMPLOYEE="employee"
    ADMIN="admin"

class Gender(str,enum.Enum):
    MALE="male"
    FEMALE="female"
    OTHER="other"

class ShiftType(str,enum.Enum):
    DAY="day"
    NIGHT="night"

class BookingStatus(str,enum.Enum):
    ACTIVE="active"
    CANCELLED="cancelled"