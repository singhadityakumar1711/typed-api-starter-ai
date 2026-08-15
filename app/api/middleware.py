import logging
import time
import uuid

from fastapi import Request

from app.core.logging import request_id_context

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    token = request_id_context.set(request_id)

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration = time.perf_counter() - start_time

        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        duration = time.perf_counter() - start_time

        logger.exception(
            "request_failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        raise

    finally:
        request_id_context.reset(token)