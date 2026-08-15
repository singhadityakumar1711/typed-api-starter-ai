# Typed API Starter Kit --- Development Log

This document records the steps completed so far while building the
**Typed API Starter Kit**.

The goal of the project is to create a reusable FastAPI template that
can become the foundation for future backend and AI-engineering
projects.

## Project Goal

The target starter kit will eventually include:

-   FastAPI
-   Pydantic Settings
-   Structured logging
-   Pytest scaffolding
-   Docker
-   Docker Compose
-   PostgreSQL
-   Redis
-   Pre-commit hooks
-   GitHub Actions CI
-   Linting and formatting
-   A reusable project structure

The work completed so far covers project bootstrapping, configuration
management, API routing, testing, and the first version of structured
logging.

------------------------------------------------------------------------

# 1. Project Bootstrap

## 1.1 Create the project with `uv`

We started by using `uv` as the Python project and dependency manager.

### Commands

``` powershell
uv init typed-api-starter
cd typed-api-starter
```

`uv init` creates the project and, importantly, creates the
`pyproject.toml`.

This matters because commands such as `uv add` expect a Python project
with a `pyproject.toml`.

A previous problem encountered during FastAPI setup was:

``` text
No pyproject.toml found
```

The underlying lesson is:

``` text
uv init
    ↓
creates pyproject.toml
    ↓
uv add <dependency>
```

------------------------------------------------------------------------

# 2. Initial Project Structure

The default `main.py` created by `uv init` was removed because the
project would use a proper application package.

### Remove generated `main.py`

``` powershell
Remove-Item main.py
```

### Create application directories

``` powershell
mkdir app
mkdir app\core
mkdir app\api
mkdir app\api\routes
mkdir tests
```

### Create Python package files

``` powershell
New-Item app\__init__.py
New-Item app\core\__init__.py
New-Item app\api\__init__.py
New-Item app\api\routes\__init__.py
New-Item tests\__init__.py
```

The initial structure became:

``` text
typed-api-starter/
│
├── app/
│   ├── __init__.py
│   ├── core/
│   │   └── __init__.py
│   │
│   └── api/
│       ├── __init__.py
│       └── routes/
│           └── __init__.py
│
├── tests/
│   └── __init__.py
│
├── .gitignore
├── .python-version
├── README.md
└── pyproject.toml
```

------------------------------------------------------------------------

# 3. Install FastAPI

FastAPI was added as a project dependency.

### Command

``` powershell
uv add "fastapi[standard]"
```

This performs two important operations:

1.  Adds FastAPI to `pyproject.toml`.
2.  Resolves and records dependencies in `uv.lock`.

Conceptually:

``` text
pyproject.toml
      │
      ▼
uv add
      │
      ├── dependency declaration
      │
      └── dependency resolution
               │
               ▼
            uv.lock
```

------------------------------------------------------------------------

# 4. First FastAPI Application

We created:

``` text
app/main.py
```

### Command

``` powershell
New-Item app\main.py
```

### `app/main.py`

``` python
from fastapi import FastAPI

app = FastAPI(title="Typed API Starter")


@app.get("/")
async def root():
    return {"message": "Typed API Starter is running"}
```

The application was then run with:

``` powershell
uv run fastapi dev app/main.py
```

The development server runs on:

``` text
http://127.0.0.1:8000
```

The automatically generated Swagger/OpenAPI documentation is available
at:

``` text
http://127.0.0.1:8000/docs
```

At this point the application was intentionally simple.

------------------------------------------------------------------------

# 5. Pydantic Settings

The next step was centralizing application configuration.

## 5.1 Install `pydantic-settings`

``` powershell
uv add pydantic-settings
```

The reason for using Pydantic Settings instead of repeatedly calling:

``` python
os.getenv("DATABASE_URL")
```

is that configuration becomes:

-   centralized
-   typed
-   validated
-   configurable through environment variables
-   easier to test
-   reusable across projects

The intended configuration flow is:

``` text
.env / environment variables
          │
          ▼
   Pydantic Settings
          │
          ▼
   Validated Settings
          │
          ▼
     Application
```

------------------------------------------------------------------------

# 6. Create the Settings Module

We created:

``` text
app/core/config.py
```

### Command

``` powershell
New-Item app\core\config.py
```

### `app/core/config.py`

``` python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Typed API Starter"
    environment: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/typed_api_starter"
    )
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Important concepts

### `BaseSettings`

``` python
class Settings(BaseSettings):
```

allows values to be loaded from environment variables.

For example:

``` python
debug: bool = True
```

can be overridden by:

``` env
DEBUG=false
```

Pydantic converts the environment value into the declared Python type.

### Environment variable mapping

By default:

``` text
app_name       → APP_NAME
environment    → ENVIRONMENT
debug          → DEBUG
database_url   → DATABASE_URL
redis_url      → REDIS_URL
```

### `SettingsConfigDict`

``` python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)
```

tells Pydantic Settings to read configuration from `.env`.

### `lru_cache`

``` python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

means that the settings object is created once and reused.

Conceptually:

``` text
First get_settings()
       ↓
Create Settings
       ↓
Cache object

Later get_settings()
       ↓
Return cached object
```

This is useful when Settings is used as a FastAPI dependency.

------------------------------------------------------------------------

# 7. Environment Files

We created the local environment file.

### Command

``` powershell
New-Item .env
```

### `.env`

``` env
APP_NAME=Typed API Starter
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/typed_api_starter
REDIS_URL=redis://localhost:6379/0
```

The `.env` file is intended for local configuration.

It should not be committed to Git because real projects will eventually
contain secrets such as:

``` env
OPENAI_API_KEY=...
DATABASE_URL=...
SECRET_KEY=...
```

------------------------------------------------------------------------

# 8. `.env.example`

We created a template for environment variables.

### Command

``` powershell
New-Item .env.example
```

### `.env.example`

``` env
APP_NAME=Typed API Starter
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/typed_api_starter
REDIS_URL=redis://localhost:6379/0
```

The distinction is:

``` text
.env
    ↓
actual local configuration
    ↓
should not be committed

.env.example
    ↓
configuration template
    ↓
safe to commit
```

We also ensured `.gitignore` contains:

``` gitignore
.env
```

------------------------------------------------------------------------

# 9. Connect Settings to FastAPI

`app/main.py` was updated to use the settings system.

### `app/main.py`

``` python
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.environment,
    }
```

The application was run using:

``` powershell
uv run fastapi dev app/main.py
```

This demonstrated that `.env` values could override the Python defaults.

For example:

``` env
APP_NAME=My Experimental API
ENVIRONMENT=local
DEBUG=false
```

would cause the application to use those values.

------------------------------------------------------------------------

# 10. API Architecture with `APIRouter`

The next architectural improvement was separating endpoint definitions
from `main.py`.

The target structure became:

``` text
app/
├── main.py
│
├── core/
│   └── config.py
│
└── api/
    ├── router.py
    └── routes/
        └── health.py
```

The architectural responsibilities are:

``` text
main.py
    ↓
application composition

router.py
    ↓
route aggregation

health.py
    ↓
actual endpoint implementation
```

------------------------------------------------------------------------

# 11. Health Router

We created:

``` text
app/api/routes/health.py
```

### Command

``` powershell
New-Item app\api\routes\health.py
```

### `app/api/routes/health.py`

``` python
from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():
    return {"status": "ok"}
```

## `APIRouter`

`APIRouter` is a way of grouping related API endpoints.

For example:

``` python
router = APIRouter(
    prefix="/health",
    tags=["Health"],
)
```

means endpoints registered on this router will have:

``` text
/health
```

as their prefix.

The `tags` value is primarily used for generated API documentation.

------------------------------------------------------------------------

# 12. API Router Aggregator

We then created:

``` text
app/api/router.py
```

### Command

``` powershell
New-Item app\api\router.py
```

### `app/api/router.py`

``` python
from fastapi import APIRouter

from app.api.routes.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router)
```

This gives us a central location for aggregating API routers.

------------------------------------------------------------------------

# 13. Updated `main.py`

`app/main.py` became:

``` python
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
```

Because:

``` text
main.py
    prefix = /api/v1

api_router
    includes health_router

health_router
    prefix = /health
```

the resulting endpoint is:

``` text
GET /api/v1/health
```

The response is:

``` json
{
    "status": "ok"
}
```

The API versioning structure gives us room for future versions:

``` text
/api/v1/chat
/api/v1/documents
/api/v1/agents
```

and potentially later:

``` text
/api/v2/chat
```

without immediately breaking existing clients.

------------------------------------------------------------------------

# 14. Pytest Scaffolding

The next phase established automated API testing.

We installed:

``` powershell
uv add --dev pytest httpx
```

The `--dev` flag means these are development/test dependencies rather
than runtime dependencies.

Conceptually:

``` text
Runtime dependencies
├── fastapi
└── pydantic-settings

Development dependencies
├── pytest
└── httpx
```

------------------------------------------------------------------------

# 15. First Health Test

We created:

``` text
tests/test_health.py
```

### Command

``` powershell
New-Item tests\test_health.py
```

Initial test:

``` python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

The test is run with:

``` powershell
uv run pytest
```

Expected result:

``` text
1 passed
```

------------------------------------------------------------------------

# 16. Understanding `TestClient`

`TestClient` lets us test the FastAPI application without manually
starting Uvicorn.

The test flow is conceptually:

``` text
pytest
  ↓
TestClient
  ↓
FastAPI application
  ↓
APIRouter
  ↓
/api/v1/health
  ↓
response
```

It does not require:

``` text
pytest
   ↓
localhost:8000
   ↓
Uvicorn
```

This keeps API tests fast and self-contained.

------------------------------------------------------------------------

# 17. Separate Test Assertions

We then split the test into two tests:

``` python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_status_code():
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_check_response():
    response = client.get("/api/v1/health")

    assert response.json() == {"status": "ok"}
```

Running:

``` powershell
uv run pytest
```

should result in:

``` text
2 passed
```

------------------------------------------------------------------------

# 18. Pytest Fixture

We then introduced a shared pytest fixture.

Created:

``` text
tests/conftest.py
```

### Command

``` powershell
New-Item tests\conftest.py
```

### `tests/conftest.py`

``` python
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
```

The health tests were changed to:

``` python
def test_health_check_status_code(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_check_response(client):
    response = client.get("/api/v1/health")

    assert response.json() == {"status": "ok"}
```

Pytest sees the `client` argument and automatically injects the fixture
from `conftest.py`.

Conceptually:

``` text
test function
     │
     │ requests "client"
     ▼
pytest
     │
     ▼
@pytest.fixture
def client()
     │
     ▼
TestClient(app)
```

This dependency-injection pattern becomes increasingly valuable as the
test suite grows.

Future fixtures could provide:

-   database sessions
-   Redis clients
-   authenticated clients
-   test settings
-   mocked LLM clients
-   temporary resources

------------------------------------------------------------------------

# 19. Structured Logging

The next major phase was structured logging.

The desired architecture is:

``` text
HTTP Request
     │
     ▼
FastAPI
     │
     ├── request ID
     ├── method
     ├── path
     ├── status code
     └── duration
             │
             ▼
       structured log
```

Instead of:

``` text
Health check called
```

we want machine-readable output such as:

``` json
{
  "level": "INFO",
  "event": "request_completed",
  "method": "GET",
  "path": "/api/v1/health",
  "status_code": 200,
  "duration_ms": 3.21
}
```

Structured logging is particularly useful for AI systems because one
request can involve multiple operations:

``` text
API request
   ↓
Agent
   ↓
LLM
   ↓
Tool call
   ↓
Database
   ↓
Vector database
   ↓
LLM
```

A request ID allows these events to be correlated.

------------------------------------------------------------------------

# 20. Logging Components

Python's logging architecture has four important components:

``` text
Logger
   ↓
LogRecord
   ↓
Handler
   ↓
Formatter
   ↓
output
```

## Logger

Created with:

``` python
logger = logging.getLogger(__name__)
```

The logger identifies the module producing the event.

For example:

``` text
app.api.routes.health
```

## LogRecord

When code calls:

``` python
logger.info("health_check_called")
```

Python creates a `LogRecord`.

It represents the logging event and contains information such as:

-   logger name
-   level
-   message
-   timestamp-related information
-   filename
-   module
-   function
-   line number
-   exception information
-   custom fields

## Handler

A handler determines where the log goes.

We used:

``` python
logging.StreamHandler(sys.stdout)
```

which sends logs to standard output.

Other handlers can write to files or other destinations.

## Formatter

A formatter determines how a `LogRecord` is represented.

We created a custom JSON formatter so logs can be consumed by log
collectors and observability systems.

------------------------------------------------------------------------

# 21. Custom JSON Formatter

We created:

``` text
app/core/logging.py
```

### Command

``` powershell
New-Item app\core\logging.py
```

### Initial `app/core/logging.py`

``` python
import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
```

------------------------------------------------------------------------

# 22. Configure Logging in `main.py`

`app/main.py` was updated:

``` python
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)
```

The logging configuration is initialized when the application module is
loaded.

------------------------------------------------------------------------

# 23. Add a Logger to the Health Endpoint

`app/api/routes/health.py` was updated:

``` python
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():
    logger.info("health_check_called")

    return {"status": "ok"}
```

The logger is named using:

``` python
logging.getLogger(__name__)
```

which means the logger name reflects the module.

For this file it will be approximately:

``` text
app.api.routes.health
```

------------------------------------------------------------------------

# 24. Request Logging Middleware

We then added middleware for HTTP request-level logging.

Created:

``` text
app/api/middleware.py
```

### Command

``` powershell
New-Item app\api\middleware.py
```

### Initial middleware

``` python
import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )

    response.headers["X-Request-ID"] = request_id

    return response
```

------------------------------------------------------------------------

# 25. Understanding Middleware

Middleware wraps request processing.

Conceptually:

``` text
Client
   │
   ▼
Middleware
   │
   ▼
FastAPI routing
   │
   ▼
Endpoint
   │
   ▼
Response
   │
   ▼
Middleware
   │
   ▼
Client
```

The important line is:

``` python
response = await call_next(request)
```

`call_next` continues processing the request through the rest of the
middleware chain and eventually the endpoint.

This lets us measure the time spent processing the request.

------------------------------------------------------------------------

# 26. Measuring Request Duration

We use:

``` python
start_time = time.perf_counter()

response = await call_next(request)

duration = time.perf_counter() - start_time
```

Conceptually:

``` text
t0 ───────────────────────────── t1
       endpoint processing
```

`time.perf_counter()` is appropriate for measuring elapsed duration.

We convert seconds to milliseconds:

``` python
duration_ms = duration * 1000
```

The resulting log can contain:

``` text
duration_ms = 3.42
```

This becomes useful for identifying slow:

-   API endpoints
-   database calls
-   Redis calls
-   LLM calls
-   external APIs

------------------------------------------------------------------------

# 27. Request IDs

The middleware creates:

``` python
request_id = str(uuid.uuid4())
```

This gives each HTTP request a unique identifier.

We then return it to the client:

``` python
response.headers["X-Request-ID"] = request_id
```

So a response contains something like:

``` text
X-Request-ID: 8f8c6c19-...
```

If a client reports a problem, that ID can eventually be used to find
the corresponding logs.

------------------------------------------------------------------------

# 28. Structured Fields with `extra`

The middleware uses:

``` python
logger.info(
    "request_completed",
    extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
    },
)
```

The `extra` dictionary adds custom attributes to the `LogRecord`.

Conceptually:

``` text
LogRecord
├── level = INFO
├── message = request_completed
├── logger = app.api.middleware
├── request_id = abc123
├── method = GET
├── path = /api/v1/health
├── status_code = 200
└── duration_ms = 2.41
```

This is a core concept behind structured logging.

------------------------------------------------------------------------

# 29. Updated JSON Formatter for Custom Fields

The formatter was expanded so `extra` fields are included.

### `app/core/logging.py`

``` python
import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        standard_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }

        for key, value in record.__dict__.items():
            if key not in standard_fields:
                log_record[key] = value

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
```

This allows fields passed using `extra=` to become part of the JSON
output.

------------------------------------------------------------------------

# 30. Register the Middleware

`app/main.py` was updated again:

``` python
from fastapi import FastAPI

from app.api.middleware import request_logging_middleware
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.middleware("http")(request_logging_middleware)

app.include_router(
    api_router,
    prefix="/api/v1",
)
```

The middleware now wraps every HTTP request handled by the application.

------------------------------------------------------------------------

# 31. Current Logging Flow

The current architecture is:

``` text
HTTP request
      │
      ▼
request_logging_middleware
      │
      ├── generate request ID
      ├── record start time
      │
      ▼
   FastAPI endpoint
      │
      ├── endpoint-specific logger
      │
      ▼
    response
      │
      ▼
middleware
      │
      ├── calculate duration
      ├── log request_completed
      └── attach X-Request-ID
```

The logging pipeline itself is:

``` text
logger.info(...)
      │
      ▼
   LogRecord
      │
      ▼
   Handler
      │
      ▼
 JSONFormatter
      │
      ▼
   stdout
```

------------------------------------------------------------------------

# 32. Important Logging Design Issue Identified

The current implementation has an important limitation.

The request ID is created in middleware:

``` python
request_id = str(uuid.uuid4())
```

but only explicitly added to the request-completed log.

Suppose the application later does:

``` python
logger.error("LLM request failed")
```

inside another module.

That logger does not automatically know the current request ID.

We therefore identified the next logging improvement:

``` text
HTTP request
      │
      ▼
request_id
      │
      ▼
ContextVar
      │
      ├── API route
      ├── service
      ├── repository
      ├── Redis
      └── LLM client
              │
              ▼
          structured logs
```

Python's `contextvars` module can provide request-scoped context without
passing `request_id` through every function.

This is the **next step** in the project.

------------------------------------------------------------------------

# 33. Current Project Structure

At the end of the completed work, the project should look approximately
like:

``` text
typed-api-starter/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── middleware.py
│       ├── router.py
│       │
│       └── routes/
│           ├── __init__.py
│           └── health.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_health.py
│
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
└── uv.lock
```

------------------------------------------------------------------------

# 34. Commands Used So Far

For convenience, here is the complete CLI sequence we used.

## Project creation

``` powershell
uv init typed-api-starter
cd typed-api-starter
```

## Remove generated entry point

``` powershell
Remove-Item main.py
```

## Create directories

``` powershell
mkdir app
mkdir app\core
mkdir app\api
mkdir app\api\routes
mkdir tests
```

## Create package files

``` powershell
New-Item app\__init__.py
New-Item app\core\__init__.py
New-Item app\api\__init__.py
New-Item app\api\routes\__init__.py
New-Item tests\__init__.py
```

## Install FastAPI

``` powershell
uv add "fastapi[standard]"
```

## Run FastAPI

``` powershell
uv run fastapi dev app/main.py
```

## Install settings

``` powershell
uv add pydantic-settings
```

## Create settings

``` powershell
New-Item app\core\config.py
```

## Create environment files

``` powershell
New-Item .env
New-Item .env.example
```

## Create API modules

``` powershell
New-Item app\api\routes\health.py
New-Item app\api\router.py
```

## Install test dependencies

``` powershell
uv add --dev pytest httpx
```

## Create tests

``` powershell
New-Item tests\test_health.py
New-Item tests\conftest.py
```

## Run tests

``` powershell
uv run pytest
```

## Create logging modules

``` powershell
New-Item app\core\logging.py
New-Item app\api\middleware.py
```

## Run the application

``` powershell
uv run fastapi dev app/main.py
```

## Run the test suite

``` powershell
uv run pytest
```

------------------------------------------------------------------------

# 35. What We Have Learned

The project has already covered several important professional concepts.

### Python / tooling

-   `uv init`
-   `uv add`
-   `uv.lock`
-   runtime vs development dependencies
-   project structure

### FastAPI

-   `FastAPI`
-   `APIRouter`
-   route prefixes
-   API tags
-   API versioning
-   middleware
-   dependency injection concepts

### Pydantic

-   `BaseSettings`
-   environment variables
-   type validation
-   `.env`
-   configuration centralization
-   cached settings

### Testing

-   pytest
-   `TestClient`
-   API testing without running Uvicorn
-   pytest fixtures
-   `conftest.py`
-   dependency injection in tests

### Logging

-   Logger
-   LogRecord
-   Handler
-   Formatter
-   log levels
-   structured logging
-   JSON logs
-   request IDs
-   middleware
-   request duration
-   `logging.extra`

------------------------------------------------------------------------

# 36. Next Steps

The next development step should be:

## Phase 5 continuation --- Production-quality logging

Implement:

``` text
ContextVar
    ↓
request-scoped request ID
    ↓
automatic request ID in all logs
```

Then move to:

## Phase 6 --- Docker + PostgreSQL + Redis

The target architecture will become:

``` text
                  Docker Compose
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
      FastAPI       PostgreSQL      Redis
       API
```

After that:

``` text
Phase 7  → Dockerize API properly
Phase 8  → Pre-commit
Phase 9  → GitHub Actions CI
Phase 10 → Template hardening
```

The ultimate goal is to make this repository reusable as the starting
point for future backend and AI-engineering projects.

---

# 40. Phase 6 — Docker + PostgreSQL + Redis: Infrastructure Setup

We then began Phase 6 of the project: introducing containerized infrastructure with Docker Compose.

The target architecture is:

```text
                    Docker Compose
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       FastAPI       PostgreSQL       Redis
       container       container      container
          │              │              │
          └──────────────┴──────────────┘
                 Docker network
```

The first step was intentionally to run PostgreSQL and Redis independently of FastAPI. This lets us verify the infrastructure before adding the API container.

## 40.1 Create `docker-compose.yml`

At the project root:

```text
typed-api-starter/
├── app/
├── tests/
├── .env
├── .env.example
├── pyproject.toml
├── uv.lock
└── docker-compose.yml
```

Create the file in PowerShell:

```powershell
New-Item docker-compose.yml
```

The initial Compose configuration was:

```yaml
services:

  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: typed_api_starter
    ports:
      - "5432:5432"

  redis:
    image: redis:8
    ports:
      - "6379:6379"
```

---

# 41. Docker Compose Concepts

Docker Compose lets us describe the local infrastructure of the project in one declarative file.

Instead of manually running separate containers such as:

```text
docker run postgres ...
docker run redis ...
```

we can use:

```powershell
docker compose up -d
```

and:

```powershell
docker compose down
```

The Compose file therefore acts as an infrastructure definition for the project.

The services currently defined are:

```yaml
services:
  postgres:
    ...

  redis:
    ...
```

The names `postgres` and `redis` are important because they become service names that other containers can use for Docker-network communication.

---

# 42. PostgreSQL Service

The PostgreSQL service uses:

```yaml
postgres:
  image: postgres:17
```

This tells Docker to create a container from the PostgreSQL 17 image.

Conceptually:

```text
PostgreSQL image
       │
       │ Docker Compose
       ▼
PostgreSQL container
```

If the image does not already exist locally, Docker attempts to pull it from the configured container registry.

---

# 43. PostgreSQL Environment Variables

The PostgreSQL image was configured with:

```yaml
environment:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  POSTGRES_DB: typed_api_starter
```

These initialize the local development database.

Conceptually:

```text
PostgreSQL
│
├── User
│    └── postgres
│
├── Password
│    └── postgres
│
└── Database
     └── typed_api_starter
```

These credentials are suitable only for local development. They should eventually be supplied through environment variables rather than being hard-coded in the Compose file, especially for production deployments.

---

# 44. PostgreSQL Port Mapping

The configuration:

```yaml
ports:
  - "5432:5432"
```

uses the format:

```text
HOST_PORT:CONTAINER_PORT
```

Therefore:

```text
Your Windows machine
localhost:5432
       │
       ▼
PostgreSQL container
      :5432
```

This allows software running directly on the host machine to connect to PostgreSQL.

However, this is different from how containers communicate with each other.

Inside the Docker network, the FastAPI container will eventually use:

```text
postgres:5432
```

rather than:

```text
localhost:5432
```

---

# 45. Docker Networking: `localhost` vs Service Names

This is one of the most important Docker concepts introduced in this phase.

Inside a FastAPI container:

```text
localhost
    ↓
the FastAPI container itself
```

Therefore, once FastAPI is containerized, this URL would be wrong for PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/typed_api_starter
```

The correct container-to-container address will be:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/typed_api_starter
```

Similarly, Redis will eventually be accessed as:

```env
REDIS_URL=redis://redis:6379/0
```

The Compose service names act as DNS names inside the Docker network:

```text
FastAPI
   │
   ├── postgres:5432
   │
   └── redis:6379
```

---

# 46. PostgreSQL Persistent Storage

The PostgreSQL service was then updated to use a named Docker volume:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

and the volume was declared at the bottom of the Compose file:

```yaml
volumes:
  postgres_data:
```

The resulting mapping is:

```text
Docker named volume                  PostgreSQL container
────────────────────                 ─────────────────────────
postgres_data  ───────────────────> /var/lib/postgresql/data
```

PostgreSQL stores its database files under:

```text
/var/lib/postgresql/data
```

inside the container. Docker mounts the named volume at that location so that the database data survives container recreation.

---

# 47. Where the PostgreSQL Data Actually Lives on Windows

Because development is being performed on Windows with Docker Desktop and its Linux/WSL-based container environment, the named volume is managed inside Docker's Linux environment rather than appearing as a normal project directory.

Conceptually:

```text
Physical Windows disk
        │
        ▼
Windows
        │
        ▼
Docker Desktop / WSL 2
        │
        ▼
Docker's Linux filesystem
        │
        ▼
Docker named volume
postgres_data
        │
        ▼
PostgreSQL data
```

The volume ultimately consumes physical disk space on the Windows machine, but Docker manages the underlying storage.

It should not be treated as a normal folder such as:

```text
C:\Users\ASUS\Desktop\AI Roadmap\sample-projects\typed-api-starter\postgres_data
```

To inspect the volume:

```powershell
docker volume ls
```

and:

```powershell
docker volume inspect typed-api-starter_postgres_data
```

The exact volume name may be prefixed by the Compose project name.

A typical inspection result contains a Linux mountpoint similar to:

```text
/var/lib/docker/volumes/typed-api-starter_postgres_data/_data
```

That path belongs to Docker's Linux environment rather than being a normal Windows project path.

---

# 48. Named Volume vs Bind Mount

We explicitly discussed the difference between a Docker-managed named volume and a host bind mount.

## Named volume — current approach

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

Conceptually:

```text
Windows disk
   └── Docker/WSL managed storage
          └── postgres_data
```

## Bind mount — alternative

```yaml
volumes:
  - ./postgres_data:/var/lib/postgresql/data
```

This would expose a normal project directory:

```text
typed-api-starter/
└── postgres_data/
```

For our starter kit, the named volume is the preferred default because Docker manages the database storage lifecycle without exposing PostgreSQL's internal data directory directly in the source repository.

---

# 49. PostgreSQL Data Persistence

The important distinction is:

```powershell
docker compose down
```

removes the containers but does not normally remove the named volume.

Therefore the database data remains available when the services are recreated.

However:

```powershell
docker compose down -v
```

also removes the declared named volumes.

For this project, that means the PostgreSQL data in `postgres_data` is deleted.

This command should therefore be used carefully.

---

# 50. Why Redis Does Not Have a Volume Yet

Redis was intentionally kept simple at this stage:

```yaml
redis:
  image: redis:8
  ports:
    - "6379:6379"
```

For the starter kit, Redis will initially serve purposes such as caching, temporary state, or coordination. We do not yet require Redis persistence.

If a future project requires durable Redis data, Redis persistence mechanisms such as RDB or AOF can be configured.

---

# 51. Health Checks

The Compose configuration was improved with health checks so that Docker can determine whether the services are actually ready rather than merely whether their containers have started.

The final infrastructure configuration at this stage is:

```yaml
services:

  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: typed_api_starter
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d typed_api_starter"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:8
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5


volumes:
  postgres_data:
```

---

# 52. PostgreSQL Health Check

PostgreSQL uses:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d typed_api_starter"]
  interval: 5s
  timeout: 5s
  retries: 5
```

The command:

```text
pg_isready -U postgres -d typed_api_starter
```

checks whether PostgreSQL is accepting connections for the configured user and database.

This matters because:

```text
Container started
      ↓
PostgreSQL initializing
      ↓
Database ready
```

Container startup does not necessarily mean the database is immediately ready to accept connections.

---

# 53. Redis Health Check

Redis uses:

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 5s
  retries: 5
```

Docker executes:

```text
redis-cli ping
```

inside the Redis container.

A healthy Redis server responds with:

```text
PONG
```

Therefore Docker can distinguish between a running Redis container and a Redis service that is actually responding.

---

# 54. Docker Commands Used

Start the Compose services in detached mode:

```powershell
docker compose up -d
```

View service status:

```powershell
docker compose ps
```

View all Compose logs:

```powershell
docker compose logs
```

View PostgreSQL logs:

```powershell
docker compose logs postgres
```

View Redis logs:

```powershell
docker compose logs redis
```

Stop and remove the Compose containers:

```powershell
docker compose down
```

Stop and remove containers plus declared volumes:

```powershell
docker compose down -v
```

List Docker volumes:

```powershell
docker volume ls
```

Inspect the PostgreSQL volume:

```powershell
docker volume inspect typed-api-starter_postgres_data
```

Inspect Docker disk usage:

```powershell
docker system df
```

---

# 55. Docker Desktop Connection Issue Encountered

When the Compose stack was first started, Docker returned:

```text
unable to get image 'postgres:17': error during connect:
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/postgres:17/json":
open //./pipe/dockerDesktopLinuxEngine:
The system cannot find the file specified.
```

This was diagnosed as a Docker Desktop / Docker Linux engine connectivity problem rather than a problem with `docker-compose.yml`.

The recommended diagnostic sequence was:

```powershell
docker version
docker info
docker run hello-world
docker compose up -d
docker compose ps
```

The important distinction is that `docker version` should show both client and server information when the Docker engine is reachable.

If Docker Desktop is not running, the CLI can be installed and available while still being unable to communicate with the Docker engine.

---

# 56. Current Phase 6 Architecture

At this point, the intended local infrastructure is:

```text
                       Docker Compose
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
          PostgreSQL                    Redis
          postgres:17                   redis:8
              │                            │
              │                            │
              ▼                            │
      postgres_data volume                 │
              │                            │
              └──────── Docker network ────┘
```

From the Windows host:

```text
localhost:5432 → PostgreSQL
localhost:6379 → Redis
```

From a future FastAPI container:

```text
postgres:5432 → PostgreSQL
redis:6379    → Redis
```

---

# 57. Next Steps After Docker Infrastructure

The next implementation steps are:

1. Move PostgreSQL credentials from hard-coded Compose values into `.env` variables.
2. Connect those values with the existing Pydantic Settings configuration.
3. Add PostgreSQL and Redis Python client dependencies.
4. Create small infrastructure modules for database and Redis connections.
5. Verify the FastAPI application can communicate with PostgreSQL and Redis.
6. Add FastAPI itself as a Docker Compose service.
7. Add service dependencies and health-aware startup ordering.
8. Build the FastAPI Docker image.
9. Verify the complete three-service stack.

The eventual target is:

```text
                         Docker Compose
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
       FastAPI            PostgreSQL            Redis
       :8000                 :5432              :6379
          │                   │                   │
          └───────────────────┴───────────────────┘
                       internal network
```

The overall starter-kit roadmap remains:

```text
✅ Phase 1  Project bootstrap
✅ Phase 2  Pydantic Settings
✅ Phase 3  APIRouter architecture
✅ Phase 4  Pytest scaffolding
✅ Phase 5  Structured logging
    └── ContextVar-based request IDs
🟡 Phase 6  Docker + PostgreSQL + Redis
    ├── Docker Compose configuration
    ├── PostgreSQL service
    ├── Redis service
    ├── PostgreSQL named volume
    └── health checks
⬜ Phase 7  Dockerize API properly
⬜ Phase 8  Pre-commit
⬜ Phase 9  GitHub Actions CI
⬜ Phase 10 Template hardening
```
