from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.employee import Employee
from dataclasses import dataclass
from app.models.cab import Cab
from app.models.stop import Stop
from datetime import datetime
from datetime import timedelta
from app.services.routing_service import RouteResult,RoutingService
from app.services.spatial_service import (
    get_grid_cell,
    get_neighboring_cells,
    haversine_distance,
)


MAX_CANDIDATE_DISTANCE_KM = 2.0

@dataclass
class NearbyCandidate:
    employee: Employee
    distance_km: float

class PlanningService:

    def __init__(self, db: Session):
        self.db = db
    #first get all the shifts bookings
    def get_active_bookings(
        self,
        shift_id: int,
    ) -> list[Booking]:

        return (
            self.db.query(Booking)
            .filter(
                Booking.shift_id == shift_id,
                Booking.status == BookingStatus.ACTIVE,
            )
            .all()
        )
    #then craete spatial cells or table
    def group_by_spatial_cell(
        self,
        bookings: list[Booking],
    ) -> dict[tuple[int, int], list[Employee]]:

        groups = defaultdict(list)

        for booking in bookings:

            employee = booking.employee

            cell = get_grid_cell(
                employee.home_lat,
                employee.home_lng,
            )

            groups[cell].append(employee)

        return dict(groups)
    #get only neighbouring cells so we won't need to search entire grid

    def find_nearby_employees(
    self,
    employee: Employee,
    bookings: list[Booking],
    ) -> list[NearbyCandidate]:

        employee_cell = get_grid_cell(
            employee.home_lat,
            employee.home_lng,
        )

        neighboring_cells = set(
            get_neighboring_cells(employee_cell)
        )

        candidates = []

        for booking in bookings:

            candidate = booking.employee

            if candidate.id == employee.id:
                continue

            candidate_cell = get_grid_cell(
                candidate.home_lat,
                candidate.home_lng,
            )

            if candidate_cell not in neighboring_cells:
                continue

            distance = haversine_distance(
                employee.home_lat,
                employee.home_lng,
                candidate.home_lat,
                candidate.home_lng,
            )

            if distance <= MAX_CANDIDATE_DISTANCE_KM:
                candidates.append(
                    NearbyCandidate(
                        employee=candidate,
                        distance_km=distance,
                    )
                )

        candidates.sort(
            key=lambda candidate: candidate.distance_km
        )

        return candidates

    def create_cab_groups(
            self,
            bookings:list[Booking],
            capacity:int=4,
    )->list[list[Employee]]:
        employees = [
            booking.employee
            for booking in bookings
        ]
        nearby_map={}

        for employee in employees:
            nearby_map[employee.id]=(
                self.find_nearby_employees(
                    employee,
                    bookings
                )
            )

        #starting with employees with having fewest neighbour
        #becuase we will have to do clustering based on given capacity(4 or 6 here)
        #so if we start with less then we won't need to eleminate but we will do huristriccal
        unassigned={
            employee.id:employee
            for employee in employees
        }
        cab_groups=[]

        while unassigned:

            #pick the most constrained employee
            seed = min(
                unassigned.values(),
                key=lambda employee: len(
                    [
                        candidate
                        for candidate in nearby_map[employee.id]
                        if candidate.employee.id in unassigned
                    ]
                ),
            )

            group = [seed]

            #find nearest unassigned candidates
            candidates = [
                candidate
                for candidate in nearby_map[seed.id]
                if candidate.employee.id in unassigned
            ]

            # Already sorted by distance.
            # Add closest candidates until capacity.
            for candidate in candidates:

                if len(group) >= capacity:
                    break

                group.append(candidate.employee)

            #mark candidates as signed
            for employee in group:
                unassigned.pop(employee.id)

            cab_groups.append(group)
        return cab_groups
    def clear_existing_plan(self, shift_id: int):
        existing_cabs = (
            self.db.query(Cab)
            .filter(Cab.shift_id == shift_id)
            .all()
        )

        for cab in existing_cabs:
            self.db.query(Stop).filter(
                Stop.cab_id == cab.id
            ).delete()

            self.db.delete(cab)

    def save_route(
    self,
    shift_id: int,
    employee_ids: list[int],
    pickup_etas: list[datetime],
    capacity: int = 4,
) -> Cab:

        cab = Cab(
            shift_id=shift_id,
            capacity=capacity,
            guard_assigned=False,
        )

        self.db.add(cab)
        self.db.flush()

        for sequence_no, (employee_id, pickup_eta) in enumerate(
            zip(employee_ids, pickup_etas),
            start=1,
        ):
            stop = Stop(
                cab_id=cab.id,
                employee_id=employee_id,
                sequence_no=sequence_no,
                eta=pickup_eta,
                is_pickup=True,
            )

            self.db.add(stop)


        return cab

    #finding cab and stops id for cancelled booking
    def find_cab_for_booking(
    self,
    booking: Booking,
) -> Cab | None:

        stop = (
            self.db.query(Stop)
            .join(Cab, Stop.cab_id == Cab.id)
            .filter(
                Stop.employee_id == booking.employee_id,
                Cab.shift_id == booking.shift_id,
                Stop.is_pickup.is_(True),
            )
            .first()
        )

        if stop is None:
            return None

        return (
            self.db.query(Cab)
            .filter(Cab.id == stop.cab_id)
            .first()
        )
    def get_cab_employees(
    self,
    cab: Cab,
) -> list[Employee]:

        stops = (
            self.db.query(Stop)
            .filter(
                Stop.cab_id == cab.id,
                Stop.is_pickup.is_(True),
            )
            .order_by(Stop.sequence_no)
            .all()
        )

        return [
            stop.employee
            for stop in stops
        ]
    def replan_cab(
    self,
    cab: Cab,
) -> None:

        shift = cab.shift
        office = shift.office

        employees = self.get_cab_employees(cab)

        # No passengers left
        #
        if not employees:
            self.db.delete(cab)
            return

        routing_service = RoutingService()

        route = routing_service.find_best_route(
            employees,
            office,
            shift.shift_type,
        )

        route_duration = timedelta(
            minutes=route.total_time_minutes
        )

        start_time = shift.start_time - route_duration

        # Remove old stops
        self.db.query(Stop).filter(
            Stop.cab_id == cab.id
        ).delete()

        # Create new stops
        for sequence_no, (employee_id, offset) in enumerate(
            zip(
                route.employee_ids,
                route.pickup_offsets_minutes,
            ),
            start=1,
        ):
            pickup_time = (
                start_time
                + timedelta(minutes=offset)
            )

            stop = Stop(
                cab_id=cab.id,
                employee_id=employee_id,
                sequence_no=sequence_no,
                eta=pickup_time,
                is_pickup=True,
            )

            self.db.add(stop)

    def remove_employee_from_cab(
    self,
    cab_id: int,
    employee_id: int,
) -> None:

        self.db.query(Stop).filter(
            Stop.cab_id == cab_id,
            Stop.employee_id == employee_id,
            Stop.is_pickup.is_(True),
        ).delete()