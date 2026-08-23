"""Readiness probe endpoint."""

from fastapi import APIRouter, Response, status

from app.application.services.health_service import HealthService
from app.schemas.common import ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness(response: Response) -> ReadinessResponse:
    result = await HealthService().get_readiness()
    if result.status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
