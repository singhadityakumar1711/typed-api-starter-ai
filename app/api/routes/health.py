import logging

from fastapi import APIRouter, Request

from app.db.health import check_postgres, check_redis


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check(request: Request):
    postgres_ok = await check_postgres(request)
    redis_ok = await check_redis(request)

    logger.info(
        "health_check_completed",
        extra={
            "postgres": postgres_ok,
            "redis": redis_ok,
        },
    )

    return {
        "status": "ok",
        "dependencies": {
            "postgres": postgres_ok,
            "redis": redis_ok,
        },
    }