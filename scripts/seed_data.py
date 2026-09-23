from datetime import datetime

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.booking import Booking
from app.models.employee import Employee
from app.models.enums import BookingStatus, Gender, Role, ShiftType
from app.models.office import Office
from app.models.shift import Shift


EMPLOYEES = [
    {
        "name": "Test Employee 1",
        "email": "seed1@example.com",
        "gender": Gender.MALE,
        "home_lat": 31.2530,
        "home_lng": 75.7020,
    },
    {
        "name": "Test Employee 2",
        "email": "seed2@example.com",
        "gender": Gender.FEMALE,
        "home_lat": 31.2540,
        "home_lng": 75.7030,
    },
    {
        "name": "Test Employee 3",
        "email": "seed3@example.com",
        "gender": Gender.MALE,
        "home_lat": 31.2545,
        "home_lng": 75.7040,
    },
    {
        "name": "Test Employee 4",
        "email": "seed4@example.com",
        "gender": Gender.FEMALE,
        "home_lat": 31.2525,
        "home_lng": 75.7015,
    },
    {
        "name": "Test Employee 5",
        "email": "seed5@example.com",
        "gender": Gender.MALE,
        "home_lat": 31.2600,
        "home_lng": 75.7100,
    },
    {
        "name": "Test Employee 6",
        "email": "seed6@example.com",
        "gender": Gender.FEMALE,
        "home_lat": 31.2610,
        "home_lng": 75.7110,
    },
    {
        "name": "Test Employee 7",
        "email": "seed7@example.com",
        "gender": Gender.MALE,
        "home_lat": 31.2595,
        "home_lng": 75.7090,
    },
    {
        "name": "Test Employee 8",
        "email": "seed8@example.com",
        "gender": Gender.FEMALE,
        "home_lat": 31.2800,
        "home_lng": 75.7350,
    },
    {
        "name": "Test Employee 9",
        "email": "seed9@example.com",
        "gender": Gender.MALE,
        "home_lat": 31.2810,
        "home_lng": 75.7360,
    },
    {
        "name": "Test Employee 10",
        "email": "seed10@example.com",
        "gender": Gender.FEMALE,
        "home_lat": 31.2795,
        "home_lng": 75.7340,
    },
]


def seed_data():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # 1. Find the office
        # --------------------------------------------------
        office = (
            db.query(Office)
            .filter(Office.name == "LPU Main Campus")
            .first()
        )

        if not office:
            office = Office(
                name="LPU Main Campus",
                lat=31.253,
                lng=75.703,
            )

            db.add(office)
            db.commit()
            db.refresh(office)

        print(f"Office: {office.name} (id={office.id})")

        # --------------------------------------------------
        # 2. Find or create shift
        # --------------------------------------------------
        shift = (
            db.query(Shift)
            .filter(
                Shift.office_id == office.id,
                Shift.start_time == datetime(2026, 9, 24, 9, 0),
                Shift.shift_type == ShiftType.DAY,
            )
            .first()
        )

        if not shift:
            shift = Shift(
                office_id=office.id,
                start_time=datetime(2026, 9, 24, 9, 0),
                shift_type=ShiftType.DAY,
            )

            db.add(shift)
            db.commit()
            db.refresh(shift)

        print(f"Shift: {shift.id}")

        # --------------------------------------------------
        # 3. Create employees and bookings
        # --------------------------------------------------
        password = hash_password("SeedPassword123!")

        for data in EMPLOYEES:

            employee = (
                db.query(Employee)
                .filter(Employee.email == data["email"])
                .first()
            )

            if not employee:
                employee = Employee(
                    name=data["name"],
                    email=data["email"],
                    password_hash=password,
                    gender=data["gender"],
                    role=Role.EMPLOYEE,
                    home_lat=data["home_lat"],
                    home_lng=data["home_lng"],
                )

                db.add(employee)
                db.commit()
                db.refresh(employee)

                print(
                    f"Created employee: "
                    f"{employee.name} (id={employee.id})"
                )
            else:
                print(
                    f"Employee already exists: "
                    f"{employee.name} (id={employee.id})"
                )

            # ----------------------------------------------
            # Create booking if it doesn't already exist
            # ----------------------------------------------
            booking = (
                db.query(Booking)
                .filter(
                    Booking.employee_id == employee.id,
                    Booking.shift_id == shift.id,
                )
                .first()
            )

            if not booking:
                booking = Booking(
                    employee_id=employee.id,
                    shift_id=shift.id,
                    status=BookingStatus.ACTIVE,
                )

                db.add(booking)
                db.commit()

                print(
                    f"  → Created booking for "
                    f"{employee.name}"
                )

        print("\nSeed completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()