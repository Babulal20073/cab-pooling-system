from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.auth import RegisterRequest
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
class AuthService:
    def __init__(self,db:Session):
        self.db=db

    def register(self,data:RegisterRequest)->Employee:
        existing_employee = (
            self.db.query(Employee)
            .filter(Employee.email==data.email)
            .first()
        )
        if existing_employee:
            raise ValueError("Email already registered")
        employee = Employee(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            gender=data.gender,
            home_lat=data.home_lat,
            home_lng=data.home_lng
        )
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        return employee

    def login(self,email:str,password:str)->str:
        employee = (
            self.db.query(Employee)
            .filter(Employee.email==email)
            .first()
        )
        if not employee:
            raise ValueError("Invalid email or password")

        if not verify_password(password,employee.password_hash):
            raise ValueError("Invalid email or password")

        return create_access_token(
            user_id=employee.id,
            role=employee.role.value
        )
    