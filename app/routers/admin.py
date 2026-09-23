from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.core.dependencies import require_admin
from app.models.employee import Employee
from app.schemas.office import OfficeCreate,OfficeResponse
from app.services.office_service import OfficeService
from app.schemas.shift import ShiftResponse,ShiftCreate
from app.services.shift_service import ShiftService


router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/test")
def admin_test(current_user:Employee=Depends(require_admin)):
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }

@router.post("/offices",response_model=OfficeResponse,status_code=201)
def create_office(
    data:OfficeCreate,
    current_user:Employee=Depends(require_admin),
    db:Session=Depends(get_db),
):
    service=OfficeService(db)
    return service.create_office(data)

@router.post("/shifts",response_model=ShiftResponse,status_code=201)
def create_shift(
    data:ShiftCreate,
    current_user:Employee=Depends(require_admin),
    db:Session=Depends(get_db)
):
    service=ShiftService(db)
    return service.create_shift(data)
