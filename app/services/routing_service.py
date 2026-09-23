from itertools import permutations
from dataclasses import dataclass


from app.models.employee import Employee
from app.models.office import Office
from app.services.spatial_service import haversine_distance


@dataclass
class RouteResult:
    employee_ids: list[int]
    total_distance_km: float

class RoutingService:
    def __init__(self,db):
        self.db=db
    def find_best_route(
        self,
        employees: list[Employee],
        office: Office,
    ) -> RouteResult:

        best_order = None
        best_distance = float("inf")

        for permutation in permutations(employees):
            total_distance = 0.0

            # First point = first employee's home
            previous_lat = permutation[0].home_lat
            previous_lng = permutation[0].home_lng

            # Visit every employee
            for employee in permutation[1:]:
                total_distance += haversine_distance(
                    previous_lat,
                    previous_lng,
                    employee.home_lat,
                    employee.home_lng,
                )

                previous_lat = employee.home_lat
                previous_lng = employee.home_lng

            # Last employee -> office
            total_distance += haversine_distance(
                previous_lat,
                previous_lng,
                office.lat,
                office.lng,
            )

            if total_distance < best_distance:
                best_distance = total_distance
                best_order = permutation

        return RouteResult(
            employee_ids=[
                employee.id
                for employee in best_order
            ],
            total_distance_km=best_distance,
        )