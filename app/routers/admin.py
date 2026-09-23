from fastapi import APIRouter,Depends

from app.core.dependencies import require_admin
from app.models.employee import Employee

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/test")
def admin_test(current_user:Employee=Depends(require_admin)):
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }
