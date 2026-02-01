FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim-bookworm

WORKDIR /app

# Installing postgresql-client, Ref: https://www.postgresql.org/download/linux/ubuntu/
RUN apt-get update  \
    && apt-get install -y --no-install-recommends postgresql-common  \
    && yes | /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh \
    && apt-get install -y --no-install-recommends postgresql-client-18 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and scripts
COPY --from=builder /app/.venv /app/.venv
COPY scripts/ ./scripts/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Run uvicorn directly
CMD ["uvicorn", "scripts.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
