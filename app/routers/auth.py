from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.employee import Employee
from fastapi.security import OAuth2PasswordRequestForm

router =APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",status_code=status.HTTP_201_CREATED)
def register(
    data:RegisterRequest,
    db:Session=Depends(get_db),
):
    service=AuthService(db)
    employee=service.register(data)
    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "role": employee.role.value,
    }

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    token = service.login(
        email=form_data.username,
        password=form_data.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/me")
def get_me(
    current_user: Employee = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
    }