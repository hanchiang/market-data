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
* Install [python 3](https://www.python.org/downloads/)
* Create a virtual environment: `python3 -m venv venv`
* Activate virtual environment: `source venv/bin/activate`
* Install dependencies: `pip -r install requirements.txt`
* Set PYTHONPATH: `export PYTHONPATH=$(pwd)`
* Start server: `uvicorn --reload --app-dir src main:app`
  * Server runs at: `localhost:8000`
  * API documentation runs at: `localhost:8000/docs`, `localhost:8000/redoc`.

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
* background job to remove option_price that have expired
* job: largest change in open interest, most active options
* Use poetry for dependency management
* Reporting: number of stock ticker in option_price table, number of rows for each stock ticker
* Confirm whether options data is indeed a daily snapshot that includes all past trade days
* Encode response data
* Test
* Get expirations date of a stock
