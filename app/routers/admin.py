from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.core.dependencies import require_admin
from app.models.employee import Employee
from app.schemas.office import OfficeCreate,OfficeResponse
from app.services.office_service import OfficeService
from app.schemas.shift import ShiftResponse,ShiftCreate
from app.services.shift_service import ShiftService

from app.schemas.planning import PlanningResponse
from app.services.planning_service import PlanningService
from app.models.shift import Shift
from app.models.office import Office
from datetime import timedelta
from app.exceptions import ShiftNotFoundError

from app.schemas.planning import (
    PlanningResponse,
    SpatialGroup,
    NearbyEmployee,
    NearbyEmployees,
    CabGroup,
    RouteResultResponse,
    PickupETA,
)
from app.services.routing_service import RoutingService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/test")
def admin_test(current_user:Employee=Depends(require_admin)):
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }

@router.post("/offices",response_model=OfficeResponse,status_code=201)
def create_office(
    data:OfficeCreate,
    current_user:Employee=Depends(require_admin),
    db:Session=Depends(get_db),
):
    service=OfficeService(db)
    return service.create_office(data)

@router.post("/shifts",response_model=ShiftResponse,status_code=201)
def create_shift(
    data:ShiftCreate,
    current_user:Employee=Depends(require_admin),
    db:Session=Depends(get_db)
):
    service=ShiftService(db)
    return service.create_shift(data)


@router.post(
    "/shifts/{shift_id}/plan",
    response_model=PlanningResponse,
)
def plan_shift(
    shift_id: int,
    current_user: Employee = Depends(require_admin),
    db: Session = Depends(get_db),
):
    shift = (
        db.query(Shift)
        .filter(Shift.id == shift_id)
        .first()
    )

    if shift is None:
        raise ShiftNotFoundError("Shift not found")

    office = shift.office

    service = PlanningService(db)
    #clear previously generated plans
    try:
        service.clear_existing_plan(shift_id)

        bookings = service.get_active_bookings(shift_id)

        spatial_groups = service.group_by_spatial_cell(bookings)

        groups = [
            SpatialGroup(
                cell=cell,
                employee_ids=[
                    employee.id
                    for employee in employees
                ],
            )
            for cell, employees in spatial_groups.items()
        ]

        nearby = []
        #
        for booking in bookings:
            #get employees id for all the bookings
            employee = booking.employee
            #find neary employees
            candidates = service.find_nearby_employees(
                employee,
                bookings,
            )

            nearby.append(
                NearbyEmployees(
                    employee_id=employee.id,
                    nearby=[
                        NearbyEmployee(
                            employee_id=candidate.employee.id,
                            distance_km=round(
                                candidate.distance_km,
                                3,
                            ),
                        )
                        for candidate in candidates
                    ],
                )
            )
        #now cluster those into similar groups
        cab_groups = service.create_cab_groups(
            bookings,
            capacity=4,
        )

        cabs = [
            CabGroup(
                employee_ids=[
                    employee.id
                    for employee in group
                ]
            )
            for group in cab_groups
        ]
        
        routing_service = RoutingService()
        #now applying routing to the office
        routes = []

        for group in cab_groups:
            route = routing_service.find_best_route(
                group,
                office,
                shift.shift_type,
            )

            route_duration = timedelta(
                minutes=route.total_time_minutes
            )

            start_time = shift.start_time - route_duration

            pickup_times = []
            pickup_etas = []

            for employee_id, offset in zip(
                route.employee_ids,
                route.pickup_offsets_minutes,
            ):
                pickup_time = start_time + timedelta(
                    minutes=offset
                )

                pickup_times.append(pickup_time)

                pickup_etas.append(
                    PickupETA(
                        employee_id=employee_id,
                        pickup_eta=pickup_time,
                    )
                )

            # Persist Cab + Stops
            service.save_route(
                shift_id=shift_id,
                employee_ids=route.employee_ids,
                pickup_etas=pickup_times,
                capacity=4,
            )

            routes.append(
                RouteResultResponse(
                    employee_ids=route.employee_ids,
                    total_distance_km=round(
                        route.total_distance_km,
                        3,
                    ),
                    total_time_minutes=round(
                        route.total_time_minutes,
                        2,
                    ),
                    pickup_etas=pickup_etas,
                )
            )
        db.commit()
    except Exception:
        #something failed undo as we are deleting old data and in the middle if our systme is failed so that's why we do this

        db.rollback()
        raise

    return PlanningResponse(
            shift_id=shift_id,
            booking_count=len(bookings),
            groups=groups,
            nearby=nearby,
            cabs=cabs,
            routes=routes,
            message=(
                "Employees clustered and routes optimized"
            ),
        )