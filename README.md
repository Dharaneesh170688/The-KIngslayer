# GuardianAI v2 (Aegis Runtime) - Phase 1

GuardianAI v2 (Aegis Runtime) is a production-quality backend cybersecurity guardrail layer for autonomous AI agents. 

This repository contains the foundation infrastructure layer (Phase 1) including server setups, database orchestration, in-memory event buses, logging configurations, and WebSocket streaming capabilities.

## Tech Stack
- **Runtime**: Python 3.12, FastAPI
- **Dependencies**: Pydantic v2, PyYAML, python-dotenv
- **Database & ORM**: SQLAlchemy 2.0, SQLite (via `aiosqlite`)
- **WebSockets**: Standard FastAPI WebSocket implementation
- **Logging**: Rotating file logs with optional structured JSON formatting
- **Automation**: GNU Make, Docker, Docker Compose

---

## Repository Directory Structure
```
guardian-ai/
├── app/
│   ├── api/          # Versioned REST endpoints and WS connections
│   ├── core/         # Settings loading, logging configurations, exception types
│   ├── database/     # DB connections, base repository, and models
│   ├── services/     # Diagnostics, DB setup, and WS manager services
│   ├── utils/        # Prefix-IDs, datetime helpers, SHA-256 hashing
│   ├── events/       # In-memory Pub/Sub event bus
│   ├── gateway/      # Placeholder for Phase 2 intercepts
│   ├── policy/       # Placeholder for Phase 2 policy rule engines
│   ├── detectors/    # Placeholder for Phase 2 security scanners
│   ├── behavior/     # Placeholder for Phase 2 profiling
│   ├── risk/         # Placeholder for Phase 2 risk aggregation
│   ├── logger/       # Central logging placeholder
│   └── dashboard/    # Dashboard controller placeholders
├── storage/          # Local SQLite file mounts, uploads, reports
├── configs/          # Profile configuration settings (default, dev, prod)
├── contracts/        # JSON schemas validating inter-module data structures
├── examples/         # Sample HTTP scripts and websocket console code
├── docs/             # Technical design guides and deployment manuals
├── tests/            # Automated test suite
└── main.py           # Application entrypoint
```

---

## Quickstart

### 1. Environment Configurations
First, clone the project and navigate into `guardian-ai/`. Establish your local configuration by copying `.env.dev` (or `.env.example`) to `.env`:

```bash
cp .env.dev .env
```

### 2. Local Setup (Poetry)
Install dependencies and spin up the development server:

```bash
# Install dependencies
poetry install

# Run the FastAPI server locally
make run
```

The server starts at `http://127.0.0.1:8000`. You can access:
- **Interactive Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://127.0.0.1:8000/redoc`

---

## Development Automation (Makefile)
The following commands are available to streamline development tasks:

- `make run`          : Spin up the FastAPI server locally.
- `make test`         : Run all automated unit tests via Pytest.
- `make lint`         : Run Ruff and Mypy syntax and type validation checks.
- `make format`       : Format source files using Black and Ruff.
- `make clean`        : Clear compiler caches, python objects, and run cache directories.
- `make docker-up`    : Build and start the dockerized application stack.
- `make docker-down`  : Stop and tear down active docker compose services.

---

## Docker Orchestration

Build and execute the Aegis Runtime container:

```bash
docker compose up --build
```

- The container utilizes a multi-stage `Dockerfile` to create a lightweight execution environment.
- In-container database writes persist to the local host machine at `./storage/guardian.db` via a volume mount.
- Server logs write to host file `./logs/guardian.log`.
- An integrated Python-based healthcheck automatically validates container responsiveness.

---

## Testing API & WebSockets
Verify running servers using the resources in `examples/`:
- **HTTP endpoints**: Run requests inside `examples/health.http` to test `/api/v1/health`, `/api/v1/version`, and `/api/v1/status`.
- **WebSocket connection**: Connect to `ws://127.0.0.1:8000/api/v1/ws/events`. See `examples/websocket.http` for sample console test scripts.

For detailed design logs, refer to the [docs/](docs/) directory.
