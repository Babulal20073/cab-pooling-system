from pwdlib import PasswordHash
from datetime import datetime,timedelta,timezone
import jwt
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

#this tells the system that this url is having jwt token for visiting profile

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)
#this will use argon2 password hash
password_hash = PasswordHash.recommended()

def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    return password_hash.verify(password,hashed_password)


#jwt token creation
def create_access_token(user_id:int,role:str)->str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload={
        "sub":str(user_id),
        "role":role,
        "exp":expire
    }
    #header.payload.signature
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
