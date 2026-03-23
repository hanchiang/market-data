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
  * Supported local interpreter range is `>=3.12,<3.14`
  * Python 3.14 is currently not supported because `asyncpg==0.29.0` does not build cleanly there
* Copy environment template: `cp .env.example .env`
* Configure database settings in `.env`
* Install dependencies with Poetry: `poetry install --no-root`
  * `market-data-library` is resolved from the sibling directory `../market-data-library`
* Set PYTHONPATH: `export PYTHONPATH=$(pwd)`
* Run migrations before starting the app: `poetry run piccolo migrations forwards market_data_piccolo --trace`
* Start server: `poetry run uvicorn --reload --app-dir src/server main:app`
  * Server runs at: `localhost:8000`
  * API documentation runs at: `localhost:8000/docs`, `localhost:8000/redoc`.
* Legacy setup still exists for Docker and `requirements.txt`, but the tracked local development path is Poetry plus the sibling `market-data-library` repo.
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
* You can also start the full stack with `docker compose up -d`
  * Compose will start `db`, run the one-shot `migrate` service, then start `backend`
* Default local compose path uses the sibling `../market-data-library` repo:
  * `docker compose up -d db`
  * `docker compose run --rm migrate`
  * `docker compose up backend`
  * Inside compose, the backend and migration service connect to Postgres with `POSTGRES_HOST=db`
* For consumer-style testing against a git-installed `market-data-library`, build the alternate target:
  * `DOCKER_BUILDKIT=1 docker build --target dev-git --ssh default --build-arg MARKET_DATA_LIBRARY_REF=1.0.0 -t market-data:dev-git .`
  * This Git validation path requires SSH access to the private GitHub repository.

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
