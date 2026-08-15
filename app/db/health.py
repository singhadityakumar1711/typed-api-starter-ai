from fastapi import Request


async def check_postgres(request: Request) -> bool:
    pool = request.app.state.postgres_pool

    async with pool.connection() as connection:
        result = await connection.execute("SELECT 1")
        row = await result.fetchone()

    return row[0] == 1


async def check_redis(request: Request) -> bool:
    redis_client = request.app.state.redis_client

    return await redis_client.ping()