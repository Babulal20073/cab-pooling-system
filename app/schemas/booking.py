from app.models.enums import BookingStatus
from pydantic import BaseModel,ConfigDict

#as we will auto register or logged in user before requesting for booking
#so no need for register id or others 
#and we will also have shifts created so only id is required
class BookingCreate(BaseModel):
    shift_id:int

class BookingResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)#to read vlaues from orm object model to pydantic form as output
    id:int
    employee_id:int
    shift_id:int
    status:BookingStatus