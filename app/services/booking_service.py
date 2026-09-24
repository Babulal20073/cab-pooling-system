from sqlalchemy.orm import Session

from app.exceptions import(
    ShiftNotFoundError,
    DuplicateBookingError,
    BookingNotFoundError
)
from app.models.booking import Booking
from app.models.shift import Shift
from app.models.employee import Employee
from app.schemas.booking import BookingCreate
from app.models.enums import BookingStatus
from app.models.cab import Cab
from app.models.stop import Stop

class BookingService:
    def __init__(self,db:Session):
        self.db=db

    def create_booking(
            self,
            data:BookingCreate,
            employee:Employee
    )->Booking:
        #1. check whether shift exists
        shift=(
            self.db.query(Shift)
            .filter(Shift.id == data.shift_id)
            .first()
        )

        if shift is None:
            raise ShiftNotFoundError(
                "Shift not found"
            )

        #2. duplicacy checking
        existing_booking=(
            self.db.query(Booking)
            .filter(
                Booking.employee_id==employee.id,
                Booking.shift_id==data.shift_id
            )
            .first()
        )
        if existing_booking:
            raise DuplicateBookingError(
                "Employee already has a booking for this shift"
            )

        #create booking
        booking = Booking(
            employee_id=employee.id,
            shift_id=data.shift_id,
        )
        self.db.add(booking)
        return booking
    def get_my_bookings(self,employee:Employee)->list[Booking]:
        return (
            self.db.query(Booking)
            .filter(Booking.employee_id==employee.id)
            .all()
        )
    
    def cancel_booking(
    self,
    booking_id: int,
    employee: Employee,
) -> Booking:

        booking = (
            self.db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.employee_id == employee.id,
            )
            .first()
        )

        if not booking:
            raise BookingNotFoundError("Booking not found")

        if booking.status == BookingStatus.CANCELLED:
            return booking

        booking.status = BookingStatus.CANCELLED

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def cancel_booking_and_find_cab(
    self,
    booking_id: int,
    employee: Employee,
) -> tuple[Booking, Cab | None]:

        booking = (
            self.db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.employee_id == employee.id,
            )
            .first()
        )

        if not booking:
            raise BookingNotFoundError("Booking not found")

        if booking.status == BookingStatus.CANCELLED:
            return booking, None

        cab = (
            self.db.query(Cab)
            .join(Stop, Stop.cab_id == Cab.id)
            .filter(
                Stop.employee_id == booking.employee_id,
                Cab.shift_id == booking.shift_id,
                Stop.is_pickup.is_(True),
            )
            .first()
        )

        booking.status = BookingStatus.CANCELLED

        return booking, cab