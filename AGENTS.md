# market-data Agent Guide

Last verified: 2026-03-23

## Scope
- Applies to `market-data/` unless a deeper `AGENTS.md` overrides it.
- Follow the workspace root `AGENTS.md` first for cross-repo rules.

## Repo Role
- Legacy FastAPI server for stock and options data scraping plus storage.
- Uses Piccolo and Postgres or TimescaleDB-oriented tables under `market_data_piccolo/`.
- This repo is not the main notification runtime. Treat it as legacy code that still matters, not as the current operational center.

## Important Paths
- `src/server/main.py`: FastAPI entry point and route definitions.
- `src/job/stocks/`: stock scraping jobs.
- `src/job/options/`: options scraping jobs.
- `src/db/`: database startup and connection logic.
- `src/config/config.py`: required Postgres environment variables.
- `market_data_piccolo/`: schema and migration artifacts.
- `my_readme.md`: local scratchpad of useful commands and workflows for this repo. Treat it as a helpful operator reference, not canonical source of truth; validate commands against the current code and docs before relying on them.

## Repo-Specific Rules
- Verify imports and dependency wiring before changing behavior. `pyproject.toml` currently pins `market-data-library` from git, while local workflows may also use the sibling `../market-data-library` repo.
- Do not claim end-to-end runtime validation unless the database environment and library dependency path were both verified locally.
- Prefer small, targeted fixes. This repo has legacy patterns, incomplete TODOs, and little automated test coverage.
- If a change affects shared provider behavior, move or mirror the logic into `market-data-library/` instead of growing more duplicated scraper code here.

## Validation
- Minimum syntax check: `uv run python -m py_compile $(rg --files -g '*.py')`
- If you touch API routes or startup code, inspect `src/server/main.py`, `src/db/index.py`, and the environment contract in `src/config/config.py` together.
- If you touch schema-related code, review the matching table definitions and migrations under `market_data_piccolo/`.

## Stop And Ask
- The task requires changing dependency strategy for `market-data-library/`.
- The task needs live database setup or migration execution that has not been validated locally.
- The change would remove legacy behavior without confirming whether another repo still depends on it.
