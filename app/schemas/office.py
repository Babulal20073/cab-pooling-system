from pydantic import BaseModel,ConfigDict

#Before creating booking we requires some offices and shifts 
#So it's admin's responsibility so developing those first
class OfficeCreate(BaseModel):
    name:str
    lat:float
    lng:float

class OfficeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    name:str
    lat:float
    lng:float