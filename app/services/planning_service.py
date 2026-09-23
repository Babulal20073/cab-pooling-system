from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.models.employee import Employee
from dataclasses import dataclass

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

#but currently it's not doing effect of each candiate on selected neighbour candidate rather then centered or first chose candidate
