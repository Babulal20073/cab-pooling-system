from pydantic import BaseModel
from datetime import datetime

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



class PickupETA(BaseModel):
    employee_id: int
    pickup_eta: datetime

class RouteResultResponse(BaseModel):
    employee_ids: list[int]
    total_distance_km: float
    total_time_minutes: float
    pickup_etas: list[PickupETA]
    
class PlanningResponse(BaseModel):
    shift_id: int
    booking_count: int
    groups: list[SpatialGroup]
    nearby: list[NearbyEmployees]
    cabs: list[CabGroup]
    routes: list[RouteResultResponse]
    message: str

