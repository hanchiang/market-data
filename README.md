# Introduction
This project is a API service that retrieves options data for a ticker and an expiration date.  
There are 2 parts to the project:
* Scheduler:
  * `src/job/options/scraper.py`: Options data for stocks
  * `src/job/stocks/scraper.py`: Stock price
  * TODO: Most active options
  * TODO: Changes in options open interest
* API server: Serves options prices(WIP)
  * `src/server/main.py`

# Set up
* Install [Python 3.12](https://www.python.org/downloads/)
  * Supported local interpreter range is `>=3.12,<3.13`
  * Python 3.13+ is currently not supported because the released `market-data-library` dependency is pinned to Python 3.12 and `asyncpg==0.29.0` does not build cleanly on Python 3.14
* Copy environment template: `cp .env.example .env`
* Configure database settings in `.env`
* Install dependencies with Poetry: `poetry install --no-root`
  * `market-data-library` is installed from `git@github.com:hanchiang/market_data_api.git` at tag `1.5.0`
* Confirm which `market-data-library` source the repo currently imports:
  * `bash scripts/show_market_data_library_source.sh`
* Switch to the sibling workspace checkout when you need unpublished local library changes:
  * `bash scripts/use_local_market_data_library.sh`
* Switch back to the released Git dependency:
  * `bash scripts/use_git_market_data_library.sh`
* Set PYTHONPATH: `export PYTHONPATH=$(pwd)`
* Run migrations before starting the app: `poetry run piccolo migrations forwards market_data_piccolo --trace`
* Start server: `poetry run uvicorn --reload --app-dir src/server main:app`
  * Server runs at: `localhost:8000`
  * API documentation runs at: `localhost:8000/docs`, `localhost:8000/redoc`.
* Docker builds install from the same locked Poetry dependency graph as local development.
* Before using the API or scrapers, ensure Postgres is reachable and Piccolo migrations have already been applied with the configured credentials.

# Run Modes
* Dockerized DB, app running locally:
  * Start only the database: `docker compose up -d db`
  * In `.env`, set `POSTGRES_HOST=localhost`
  * Run migrations locally: `poetry run piccolo migrations forwards market_data_piccolo --trace`
  * Set `PYTHONPATH`: `export PYTHONPATH=$(pwd)`
  * Start the app locally: `poetry run uvicorn --reload --app-dir src/server main:app`
* Fully Dockerized app and DB:
  * Use the compose workflow in the Docker section below

# Docker
* Before any Docker build that needs `market-data-library`, create the build secret used by Dockerfiles:
  * `mkdir -p secret`
  * `printf '%s' "$GITHUB_TOKEN_WITH_REPO_ACCESS" > secret/github_token`
* Future CI note:
  * when this repo adds CI or CD workflows that need to install the private `market-data-library` dependency, mirror the backend repo pattern instead of hard-coding a personal token
  * provide GitHub App credentials such as `MARKET_DATA_LIBRARY_GITHUB_APP_ID` and `MARKET_DATA_LIBRARY_GITHUB_APP_PRIVATE_KEY`
  * mint a short-lived installation token in CI, then use that token for `poetry install` and any Docker `secret/github_token` build-secret step
* You can also start the full stack with `docker compose up -d`
  * Compose will start `db`, run the one-shot `migrate` service, then start `backend`
* Default local compose path uses the released git-tagged `market-data-library` package via the locked Poetry dependency graph:
  * `mkdir -p secret`
  * `printf '%s' "$GITHUB_TOKEN_WITH_REPO_ACCESS" > secret/github_token`
  * `docker compose up -d db`
  * `docker compose run --rm migrate`
  * `docker compose up backend`
  * Inside compose, the backend and migration service connect to Postgres with `POSTGRES_HOST=db`
* To make the container import the sibling workspace checkout instead, uncomment the documented `../market-data-library` bind mount plus `PYTHONPATH` override in [docker-compose.yml](docker-compose.yml) before recreating the backend container.
* To build the git-backed dev image directly:
  * `mkdir -p secret`
  * `printf '%s' "$GITHUB_TOKEN_WITH_REPO_ACCESS" > secret/github_token`
  * `docker build --secret id=github_token,src=secret/github_token --target dev-git -t market-data:dev-git .`
  * This validation path requires a GitHub token with access to the private repository.

# Operations
* Piccolo migration status check:
  * `poetry run piccolo migrations check`
* Create a new Piccolo migration:
  * `poetry run piccolo migrations new market_data_piccolo`
* Apply migrations locally:
  * `poetry run piccolo migrations forwards market_data_piccolo --trace`
* Apply migrations in Docker:
  * `docker compose run --rm migrate`
* Roll back migrations locally:
  * `poetry run piccolo migrations backwards market_data_piccolo --trace`
* Roll back all migrations locally:
  * `poetry run piccolo migrations backwards market_data_piccolo --migration_id=all --trace --auto_agree`
* Show compose service status:
  * `docker compose ps`
* Show compose logs:
  * `docker compose logs --tail 100 backend migrate db`
* Stop the Dockerized stack:
  * `docker compose down`
* Run the options scraper locally:
  * `poetry run python src/job/options/scraper.py`
* Run the stocks scraper locally:
  * `poetry run python src/job/stocks/scraper.py`

# Tech stack
* Language: Python
* Framework: FastAPI
* Database: TimescaleDB
* ORM: Piccolo

# Features
2 kinds of data:
- Aggregated data for a stock ticker(volume(total, put, call), IV, IV rank, Iv %, underlying IV 1 year high)
- Individual options data(expiration date, strike price, option type) for a stock ticker such as greeks, volatility, average volatility, volume, open interest

View options data for a ticker for an expiration date, strike price, option type, for each day(change - line graph) and total(sum - bar graph).
* volume/open interest/IV rank/IV % of option type by expiration date and strike price 
* Highest spike in volume/open interest/IV rank/IV % by expiration date and strike price

Other metrics: % change

## Options
- [ ] View how different dimensions change over time for an expiration date, strike price(+- 20 from current price)
  - [ ] High priority: Open interest, volume, IV, last, change
- [ ] Aggregate statistics for an expiration date
  - [ ] Open interest by strike price
  - [ ] Volume by strike price


## Stocks
- [ ] View how different dimensions change over time
  - [ ] bid/ask, size
  - [ ] volume
  - [ ] OHLC


# Data model
## Stock ticker table
Columns:
* id(PK) - big serial
* symbol(PK) - varchar
* name - varchar

## Stock ticker price table
* id(PK) - big serial
* symbol(FK stock ticker)
* date - date
* open_price - decimal
* high_price - decimal
* low_price - decimal
* close_price - decimal
* volume - integer

## Options price table
Store snapshot of options price for a stock ticker, expiration date, strike price, option type for every trade day
* id(PK) - big serial
* symbol - varchar
* base_symbol(FK stock ticker)
* trade_time - timestamp
* option_type - varchar
* strike_price - decimal
* open_price - decimal
* high_price - decimal
* low_price - decimal
* last_price - decimal
* moneyness - decimal
* bid_price - decimal
* midpoint - decimal
* ask_price - decimal
* volume - integer
* open_interest - integer
* volatility - decimal
* expiration_date - date
* expiration_type - varchar
* average_volatility - decimal
* delta - decimal
* theta - decimal
* gamma - decimal
* vega - decimal
* rho - decimal

## Most active options table
Store ticker that have the most options activity(open interest, volume, IV)
* id(PK) - big serial
* symbol - varchar
* last_price - decimal
* price_change - decimal
* percent_change - decimal
* options_total_volume - integer
* options_put_volume_percent - decimal
* options_call_volume_percent - decimal
* options_weighted_implied_volatility - decimal
* options_implied_volatility_rank_1y - decimal
* options_implied_volatility_percentile_1y - decimal
* underlying_implied_volatility_high_1y - decimal
* trade_time - timestamp

## Options open interest change table
Store options with the largest positive and negative open interest change
* id(PK) - big serial
* symbol - varchar
* base_symbol - varchar
* last_price - decimal
* option_type - varchar
* strike_price - decimal
* expiration_date - date
* days_to_expiration - integer
* bid_price - decimal
* midpoint - decimal
* ask_price - decimal
* last_price - decimal
* volume - integer
* open_interest - integer
* open_interest_change - integer
* volatility - decimal
* trade_time - timestamp

# TODO:
* market data library change refactor status: done
* background job to remove option_price that have expired
* job: largest change in open interest, most active options
* Reporting: number of stock ticker in option_price table, number of rows for each stock ticker
* Confirm whether options data is indeed a daily snapshot that includes all past trade days
* Encode response data
* Test
* Get expirations date of a stock
* Need to wait for timescaledb to support MACOS ventura....
