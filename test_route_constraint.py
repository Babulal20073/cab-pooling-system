from app.services.routing_service import RoutingService
from app.services.spatial_service import haversine_distance
from app.models.enums import Gender, ShiftType
from app.exceptions import NoValidRouteError


class FakeEmployee:
    def __init__(self, employee_id, lat, lng, gender=Gender.MALE):
        self.id = employee_id
        self.home_lat = lat
        self.home_lng = lng
        self.gender = gender


class FakeOffice:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng


def main():
    employees = [
        FakeEmployee(101, 31.0000, 75.0000),
        FakeEmployee(102, 32.0000, 76.0000),
        FakeEmployee(103, 33.0000, 77.0000),
    ]

    office = FakeOffice(34.0000, 78.0000)

    routing_service = RoutingService()

    try:
        route = routing_service.find_best_route(
            employees,
            office,
            ShiftType.DAY,
        )

        print("UNEXPECTED: Route was accepted")
        print(route)

    except NoValidRouteError as exc:
        print("PASS: No valid route found")
        print(exc)


if __name__ == "__main__":
    main()