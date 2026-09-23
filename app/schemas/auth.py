from pydantic import BaseModel,EmailStr

from app.models.enums import Gender

class RegisterRequest(BaseModel):
    name:str
    email:EmailStr
    password:str
    gender:Gender
    home_lat:float
    home_lng:float

#we don't require loginRequest becuase during auth we get it and password 
#using jwt form
