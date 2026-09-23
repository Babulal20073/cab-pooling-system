from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

# plan-trigger endpoint comes with ClusteringService/RoutingService — empty for now