# syntax=docker/dockerfile:1.7

FROM python:3.12-slim-bullseye AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_SYSTEM_GIT_CLIENT=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

FROM base AS deps-git

# Consumer-style builds install dependencies from the locked Poetry graph.
RUN --mount=type=secret,id=github_token git config --global \
    url."https://x-access-token:$(cat /run/secrets/github_token)@github.com/".insteadOf \
    ssh://git@github.com/ \
&& poetry install --only main --no-root \
&& rm -f /root/.gitconfig

FROM deps-git AS dev-git

COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "--app-dir", "src/server", "main:app"]
