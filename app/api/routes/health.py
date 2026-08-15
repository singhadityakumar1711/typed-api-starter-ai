import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.db.health import check_postgres, check_redis

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthDependencies(BaseModel):
    postgres: bool
    redis: bool


class HealthResponse(BaseModel):
    status: str
    dependencies: HealthDependencies


@router.get("", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    postgres_ok = await check_postgres(request)
    redis_ok = await check_redis(request)

    logger.info(
        "health_check_completed",
        extra={
            "postgres": postgres_ok,
            "redis": redis_ok,
        },
    )

    return HealthResponse(
        status="ok",
        dependencies=HealthDependencies(
            postgres=postgres_ok,
            redis=redis_ok,
        ),
    )
