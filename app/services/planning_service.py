from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.employee import Employee
from dataclasses import dataclass
from app.models.cab import Cab
from app.models.stop import Stop
from datetime import datetime

from app.services.routing_service import RouteResult

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