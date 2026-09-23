from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.init_db import init_db
from app.routers import health, auth, bookings, admin
from app.exception_handlers import (
    email_already_exists_handler,
    invalid_credentials_handler,
    office_already_exists_handler,
    office_not_found_handler,
    booking_not_found_handler,
    duplicate_booking_handler,
    shift_not_found_handler
)
from app.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    OfficeAlreadyExistsError,
    OfficeNotFoundError,
    ShiftNotFoundError,
    BookingNotFoundError,
    DuplicateBookingError
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    yield


app = FastAPI(
    title="Cab Pooling & Smart Pickup Routing",
    lifespan=lifespan,
)

app.add_exception_handler(
    EmailAlreadyExistsError,
    email_already_exists_handler,
)

app.add_exception_handler(
    InvalidCredentialsError,
    invalid_credentials_handler,
)
app.add_exception_handler(
    OfficeAlreadyExistsError,
    office_already_exists_handler,
)
app.add_exception_handler(
    OfficeNotFoundError,
    office_not_found_handler
)
app.add_exception_handler(
    ShiftNotFoundError,
    shift_not_found_handler
)
app.add_exception_handler(
    BookingNotFoundError,
    booking_not_found_handler
)
app.add_exception_handler(
    DuplicateBookingError,
    duplicate_booking_handler
)


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(admin.router)