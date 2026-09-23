from datetime import datetime
from pydantic import BaseModel
from app.models.enums import ShiftType

class ShiftCreate(BaseModel):
    office_id:int
    start_time:datetime
    shift_type:ShiftType

class ShiftResponse(BaseModel):
    id:int
    office_id:int
    start_time:datetime
    shift_type:ShiftType

