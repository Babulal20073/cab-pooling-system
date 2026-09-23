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



from app.schemas.planning import (
    PlanningResponse,
    SpatialGroup,
    NearbyEmployee,
    NearbyEmployees,
    CabGroup,
    RouteResultResponse
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
    service = PlanningService(db)

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
    #get the shift for getting the office id of shift
    shift = (
        db.query(Shift)
        .filter(Shift.id == shift_id)
        .first()
    )

    office = shift.office
    routing_service = RoutingService(db)
    #now applying routing to the office
    routes = []
    for group in cab_groups:

        route = routing_service.find_best_route(
            group,
            office,
        )

        routes.append(
            RouteResultResponse(
                employee_ids=route.employee_ids,
                total_distance_km=round(
                    route.total_distance_km,
                    3,
                ),
            )
        )

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