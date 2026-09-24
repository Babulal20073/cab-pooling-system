from datetime import datetime
from pydantic import BaseModel,ConfigDict
from app.models.enums import ShiftType

class ShiftCreate(BaseModel):
    office_id:int
    start_time:datetime
    shift_type:ShiftType

class ShiftResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)#to read vlaues from orm object model to pydantic form as output
    id:int
    office_id:int
    start_time:datetime
    shift_type:ShiftType

