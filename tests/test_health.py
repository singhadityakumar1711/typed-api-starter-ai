import pytest


@pytest.mark.asyncio
async def test_health_check_status_code(client):
    response = await client.get("/api/v1/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response(client):
    response = await client.get("/api/v1/health")

    assert response.json() == {
        "status": "ok",
        "dependencies": {
            "postgres": True,
            "redis": True,
        },
    }


@pytest.mark.asyncio
async def test_request_id_header(client):
    response = await client.get("/api/v1/health")

    assert response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_request_ids_are_unique(client):
    response_1 = await client.get("/api/v1/health")
    response_2 = await client.get("/api/v1/health")

    request_id_1 = response_1.headers["X-Request-ID"]
    request_id_2 = response_2.headers["X-Request-ID"]

    assert request_id_1 != request_id_2
