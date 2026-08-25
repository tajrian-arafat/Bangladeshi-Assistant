"""Health and readiness checks."""

from app import __version__
from app.core.config import Settings, get_settings
from app.core.database import check_database_connection
from app.schemas.common import HealthResponse, ReadinessCheck, ReadinessResponse


class HealthService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def get_health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=__version__,
            environment=self.settings.app_env,
        )

    async def get_readiness(self) -> ReadinessResponse:
        checks: list[ReadinessCheck] = []

        db_ok = await check_database_connection()
        checks.append(
            ReadinessCheck(
                name="database",
                status="ok" if db_ok else "fail",
                detail=None if db_ok else "Database connection failed",
            )
        )

        redis_ok = await self._check_redis()
        checks.append(
            ReadinessCheck(
                name="redis",
                status="ok" if redis_ok else "degraded",
                detail=None if redis_ok else "Redis unavailable (non-blocking for MVP)",
            )
        )

        overall = "ok" if db_ok else "fail"
        return ReadinessResponse(status=overall, checks=checks)

    async def _check_redis(self) -> bool:
        try:
            import redis.asyncio as redis

            client = redis.from_url(self.settings.redis_url, socket_connect_timeout=1)
            await client.ping()
            await client.aclose()
            return True
        except Exception:
            return False
