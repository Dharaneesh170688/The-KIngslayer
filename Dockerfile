# ==========================================
# Build Stage
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /build

# Copy only requirements-related files first to utilize build caching
COPY pyproject.toml README.md /build/

# Install dependencies only (no root package install yet)
RUN poetry install --only main --no-root || poetry install --no-root

# ==========================================
# Run Stage
# ==========================================
FROM python:3.12-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /workspace

# Create standard directory structures
RUN mkdir -p /workspace/storage/uploads \
             /workspace/storage/exports \
             /workspace/storage/temp \
             /workspace/storage/reports \
             /workspace/configs \
             /workspace/contracts \
             /workspace/logs

# Copy virtualenv from builder stage
COPY --from=builder /build/.venv /workspace/.venv

# Copy application source code and configurations
COPY app/ /workspace/app/
COPY configs/ /workspace/configs/
COPY contracts/ /workspace/contracts/
COPY main.py /workspace/main.py

ENV PATH="/workspace/.venv/bin:$PATH"
ENV PYTHONPATH="/workspace"

EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
