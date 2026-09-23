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
from app.services.planning_service import PlanningService

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
    booking_service = BookingService(db)
    planning_service = PlanningService(db)

    try:
        booking, cab = booking_service.cancel_booking_and_find_cab(
            booking_id,
            current_user,
        )

        if cab is not None:

            planning_service.remove_employee_from_cab(
                cab_id=cab.id,
                employee_id=booking.employee_id,
            )

            planning_service.replan_cab(cab)

        db.commit()
        db.refresh(booking)

        return booking

    except Exception:
        db.rollback()
        raise