"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    agencies,
    chat,
    conversations,
    districts,
    feedback,
    health,
    readiness,
    search,
    services,
    sources,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(readiness.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(services.router)
api_router.include_router(agencies.router)
api_router.include_router(districts.router)
api_router.include_router(districts.divisions_router)
api_router.include_router(search.router)
api_router.include_router(feedback.router)
api_router.include_router(sources.router)
api_router.include_router(admin.router)
