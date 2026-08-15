from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.middleware import request_logging_middleware
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.postgres import create_postgres_pool
from app.db.redis import create_redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres_pool = create_postgres_pool()
    redis_client = create_redis_client()

    await postgres_pool.open()
    await redis_client.ping()

    app.state.postgres_pool = postgres_pool
    app.state.redis_client = redis_client

    yield

    await redis_client.aclose()
    await postgres_pool.close()

configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

app.middleware("http")(request_logging_middleware)

app.include_router(
    api_router,
    prefix="/api/v1",
)