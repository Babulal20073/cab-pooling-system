from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.models.employee import Employee

from app.schemas.booking import (
    BookingCreate,
    BookingResponse
)
from app.services.booking_service import BookingService


router = APIRouter(prefix="/bookings",tags=["Bookings"])

@router.post(
    "",
    response_model=BookingResponse,
    status_code=201
)
def create_booking(
    data:BookingCreate,
    current_user:Employee=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    service=BookingService(db)
    return service.create_booking(data,current_user)

@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_my_bookings(
    current_user:Employee=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    service=BookingService(db)
    return service.get_my_bookings(current_user)

@router.delete(
    "/{booking_id}",
    response_model=BookingResponse
)
def cancel_booking(
    booking_id:int,
    current_user:Employee=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    service=BookingService(db)
    return service.cancel_booking(
        booking_id,
        current_user,
    )
