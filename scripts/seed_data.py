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


NIGHT_EMPLOYEE_EMAILS = {
    "seed1@example.com",
    "seed2@example.com",
    "seed3@example.com",
    "seed4@example.com",
}


def seed_data():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # 1. Find or create office
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

            print(f"Created office: {office.name} (id={office.id})")
        else:
            print(f"Office already exists: {office.name} (id={office.id})")

        # --------------------------------------------------
        # 2. Find or create DAY shift
        # --------------------------------------------------
        day_shift = (
            db.query(Shift)
            .filter(
                Shift.office_id == office.id,
                Shift.start_time == datetime(2026, 9, 24, 9, 0),
                Shift.shift_type == ShiftType.DAY,
            )
            .first()
        )

        if not day_shift:
            day_shift = Shift(
                office_id=office.id,
                start_time=datetime(2026, 9, 24, 9, 0),
                shift_type=ShiftType.DAY,
            )

            db.add(day_shift)
            db.commit()
            db.refresh(day_shift)

            print(f"Created day shift: {day_shift.id}")
        else:
            print(f"Day shift already exists: {day_shift.id}")

        # --------------------------------------------------
        # 3. Find or create NIGHT shift
        # --------------------------------------------------
        night_shift = (
            db.query(Shift)
            .filter(
                Shift.office_id == office.id,
                Shift.start_time == datetime(2026, 9, 25, 22, 0),
                Shift.shift_type == ShiftType.NIGHT,
            )
            .first()
        )

        if not night_shift:
            night_shift = Shift(
                office_id=office.id,
                start_time=datetime(2026, 9, 25, 22, 0),
                shift_type=ShiftType.NIGHT,
            )

            db.add(night_shift)
            db.commit()
            db.refresh(night_shift)

            print(f"Created night shift: {night_shift.id}")
        else:
            print(f"Night shift already exists: {night_shift.id}")

        # --------------------------------------------------
        # 4. Create employees
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

            # --------------------------------------------------
            # Create DAY booking
            # --------------------------------------------------
            day_booking = (
                db.query(Booking)
                .filter(
                    Booking.employee_id == employee.id,
                    Booking.shift_id == day_shift.id,
                )
                .first()
            )

            if not day_booking:
                day_booking = Booking(
                    employee_id=employee.id,
                    shift_id=day_shift.id,
                    status=BookingStatus.ACTIVE,
                )

                db.add(day_booking)
                db.commit()

                print(
                    f"  → Created day booking for "
                    f"{employee.name}"
                )
            else:
                print(
                    f"  → Day booking already exists for "
                    f"{employee.name}"
                )

        # --------------------------------------------------
        # 5. Create NIGHT bookings for employees 1-4
        # --------------------------------------------------
        for email in NIGHT_EMPLOYEE_EMAILS:

            employee = (
                db.query(Employee)
                .filter(Employee.email == email)
                .first()
            )

            if not employee:
                print(
                    f"Warning: employee {email} not found"
                )
                continue

            night_booking = (
                db.query(Booking)
                .filter(
                    Booking.employee_id == employee.id,
                    Booking.shift_id == night_shift.id,
                )
                .first()
            )

            if not night_booking:
                night_booking = Booking(
                    employee_id=employee.id,
                    shift_id=night_shift.id,
                    status=BookingStatus.ACTIVE,
                )

                db.add(night_booking)
                db.commit()

                print(
                    f"  → Created night booking for "
                    f"{employee.name}"
                )
            else:
                print(
                    f"  → Night booking already exists for "
                    f"{employee.name}"
                )

        print("\nSeed completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()