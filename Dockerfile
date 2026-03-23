# syntax=docker/dockerfile:1.7

FROM python:3.12-slim-bullseye AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    openssh-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS deps-local

# Local dev mode installs the sibling repo provided as a named build context.
COPY --from=market_data_library / /opt/market-data-library
RUN pip install --no-cache-dir /opt/market-data-library

FROM base AS deps-git

# Consumer-style builds can instead install the shared library from a git ref.
ARG MARKET_DATA_LIBRARY_REF=1.0.0
RUN --mount=type=ssh \
    pip install --no-cache-dir \
    "git+ssh://git@github.com/hanchiang/market_data_api.git@${MARKET_DATA_LIBRARY_REF}"

FROM deps-local AS dev-local

COPY . .
# Keep both the app and the sibling library importable for the local compose flow.
ENV PYTHONPATH=/app:/opt/market-data-library
CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "--app-dir", "src/server", "main:app"]

FROM deps-git AS dev-git

COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "--app-dir", "src/server", "main:app"]
