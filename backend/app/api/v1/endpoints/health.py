"""Health check endpoint."""

from fastapi import APIRouter

from app.application.services.health_service import HealthService
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthService().get_health()
