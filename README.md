# Introduction
This project is a API service that retrieves options data for a ticker and an expiration date.  
There are 2 parts to the project:
* Scheduler: A daily job that fetches option prices and saves it in the database
* API server: Serves options prices

# Set up
* Install [python 3](https://www.python.org/downloads/)
* Create a virtual environment: `python3 -m venv venv`
* Activate virtual environment: `source venv/bin/activate`
* Install dependencies: `pip -r install requirements.txt`
* Set PYTHONPATH: `export PYTHONPATH=$(pwd)`
* Start server: `uvicorn --reload --app-dir src main:app`
  * Server runs at: `localhost:8000`
  * API documentation runs at: `localhost:8000/docs`, `localhost:8000/redoc`.

# Tech stack
* Language: python
* Framework: FastAPI
* Database: TimescaleDB
* ORM: Piccolo

# Storage
## Postgresql 14.6
## Timescale DB 2.9.0

# Features
View options data for a ticker for an expiration date for each day, and in total.

## Options
- [ ] View how different dimensions change over time for an expiration date
  - [ ] High priority: Open interest, volume, IV, last, change
  - [ ] Medium priority: bid, ask
- [ ] Change statistics
  - [ ] Open interest by strike price
  - [ ] Volume by strike price
- [ ] Aggregate statistics
  - [ ] Open interest by strike price
  - [ ] Volume by strike price


## Stocks
- [ ] View how different dimensions change over time
  - [ ] bid/ask, size
  - [ ] volume
  - [ ] OHLC


# Data model
## Ticker table
Columns:
* symbol(PK) - varchar
* name - varchar

## Ticker price table
* id(PK) - big serial
* symbol(FK ticker)
* date - date
* open_price - decimal
* high_price - decimal
* low_price - decimal
* close_price - decimal
* volume - integer

## Options price table
* id(PK) - big serial
* symbol - varchar
* base_symbol(FK ticker)
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

# TODO:
* Scheduler
* API server
* background job to remove option_price that have expired
* new table: stock_ticker_config. Store a flag indicating whether ticker should be scraped
