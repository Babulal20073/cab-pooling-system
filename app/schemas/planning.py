from pydantic import BaseModel


class SpatialGroup(BaseModel):
    cell: tuple[int, int]
    employee_ids: list[int]


class NearbyEmployee(BaseModel):
    employee_id: int
    distance_km: float

#we will require distance at the end for clustering
class NearbyEmployees(BaseModel):
    employee_id: int
    nearby: list[NearbyEmployee]


class CabGroup(BaseModel):
    employee_ids: list[int]


class PlanningResponse(BaseModel):
    shift_id: int
    booking_count: int
    groups: list[SpatialGroup]
    nearby: list[NearbyEmployees]
    cabs: list[CabGroup]
    message: str