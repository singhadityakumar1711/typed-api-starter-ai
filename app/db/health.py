from typing import cast

from fastapi import Request


async def check_postgres(request: Request) -> bool:
    pool = request.app.state.postgres_pool

    async with pool.connection() as connection:
        result = await connection.execute("SELECT 1")
        row = await result.fetchone()

    if row is None:
        return False

    value = cast(tuple[int], row)
    return value[0] == 1


async def check_redis(request: Request) -> bool:
    redis_client = request.app.state.redis_client

    result = await redis_client.ping()

    return bool(result)
