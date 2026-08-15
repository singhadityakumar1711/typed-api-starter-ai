
from psycopg_pool import AsyncConnectionPool

from app.core.config import get_settings


def create_postgres_pool() -> AsyncConnectionPool:
    settings = get_settings()

    return AsyncConnectionPool(
        conninfo=settings.database_url,
        open=False,
    )