from app.models.employee import Employee
from app.models.enums import Gender, ShiftType


class SafetyValidator:

    def validate_night_route(
        self,
        employees: list[Employee],
        shift_type: ShiftType,
    ) -> bool:

        # Safety rule only applies to night shifts.
        if shift_type != ShiftType.NIGHT:
            return True

        # Empty route is valid from the safety perspective.
        if not employees:
            return True

        first_employee = employees[0]
        last_employee = employees[-1]

        # A woman cannot be the first pickup
        # during a night shift.
        if first_employee.gender == Gender.FEMALE:
            return False

        # A woman cannot be the final passenger
        # during a night shift.
        if last_employee.gender == Gender.FEMALE:
            return False

        return True