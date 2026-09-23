from itertools import permutations
from dataclasses import dataclass

from app.models.employee import Employee
from app.models.office import Office
from app.services.spatial_service import haversine_distance
from app.exceptions import NoValidRouteError

from app.models.enums import ShiftType
from app.services.safety_service import SafetyValidator

AVERAGE_SPEED_KMPH = 30.0
MAX_RIDE_TIME_MINUTES = 90.0


@dataclass
class RouteResult:
    employee_ids: list[int]
    total_distance_km: float
    total_time_minutes: float
    pickup_offsets_minutes: list[float]


class RoutingService:
    def __init__(self):
        self.safety_validator=SafetyValidator()
    def find_best_route(
        self,
        employees: list[Employee],
        office: Office,
        shift_type: ShiftType,

    ) -> RouteResult:

        best_order = None
        best_distance = float("inf")
        best_time = float("inf")
        best_offsets = []

        for permutation in permutations(employees):
            if not self.safety_validator.validate_night_route(
                list(permutation),
                shift_type,
            ):
                continue

            total_distance = 0.0
            leg_distances = []

            previous_lat = permutation[0].home_lat
            previous_lng = permutation[0].home_lng

            # Employee -> Employee

            for employee in permutation[1:]:

                distance = haversine_distance(
                    previous_lat,
                    previous_lng,
                    employee.home_lat,
                    employee.home_lng,
                )

                leg_distances.append(distance)
                total_distance += distance

                previous_lat = employee.home_lat
                previous_lng = employee.home_lng

            # Last employee -> Office

            office_distance = haversine_distance(
                previous_lat,
                previous_lng,
                office.lat,
                office.lng,
            )

            leg_distances.append(office_distance)
            total_distance += office_distance

            # Convert total distance to time

            total_time_minutes = (
                total_distance / AVERAGE_SPEED_KMPH
            ) * 60

            # Maximum ride-time constraint

            if total_time_minutes > MAX_RIDE_TIME_MINUTES:
                continue

            # Calculate pickup offsets

            offsets = [0.0]
            elapsed_minutes = 0.0

            for distance in leg_distances[:-1]:

                elapsed_minutes += (
                    distance / AVERAGE_SPEED_KMPH
                ) * 60

                offsets.append(elapsed_minutes)

            # Keep shortest valid route

            if total_distance < best_distance:

                best_distance = total_distance
                best_time = total_time_minutes
                best_order = permutation
                best_offsets = offsets

        # No valid route

        if best_order is None:
            raise NoValidRouteError(
                "No valid route satisfies the planning constraints"
            )

        return RouteResult(
            employee_ids=[
                employee.id
                for employee in best_order
            ],
            total_distance_km=best_distance,
            total_time_minutes=best_time,
            pickup_offsets_minutes=best_offsets,
        )