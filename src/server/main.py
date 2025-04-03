from fastapi import FastAPI
from typing import Optional

from src.db.index import run_migration, start_postgres_connection_pool, stop_postgres_connection_pool
from src.data_source.barchart import get_tradfi_api

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print('FastAPI startup event')
    await start_postgres_connection_pool()
    await run_migration()

@app.on_event('shutdown')
async def shutdown_event():
    print('FastAPI shutdown event')
    await stop_postgres_connection_pool()

@app.get("/healthz")
async def health_check():
    return {'data': 'market data is running!'}

# TODO: most active options API(symbol, name, last, change, %change, iv rank, iv%, iv 1 yr high, volume, %put, %call, put/call vol)
# TODO: Use an arg to determine whether to connect to API source or DB
@app.get("/options/{symbol}")
async def options_for_ticker(
    symbol: str, order_dir = '', expiration_type = '', expiration_date: Optional[str] = None,
    group_by: Optional[str] = '', order_by: Optional[str] = ''
):
    # TODO: initialise in fastapi startup event
    tradfi_api = await get_tradfi_api()
    data = await tradfi_api.barchart.barchart_options.get_options_for_ticker(symbol=symbol, expiration_type=expiration_type,
        expiration_date=expiration_date, group_by=group_by, order_by=order_by, order_dir=order_dir
    )

    return {'data': data}

@app.get("/options/{symbol}/expirations")
async def options_expirations_for_ticker(symbol: str):
    # TODO: cache
    # TODO: initialise in fastapi startup event
    tradfi_api = await get_tradfi_api()
    data = await tradfi_api.barchart.barchart_options.get_options_expirations_for_ticker(symbol=symbol)
    return {'data': data}

@app.get("/options-most-active")
async def most_active_options():
    # TODO: initialise in fastapi startup event
    tradfi_api = await get_tradfi_api()
    data = await tradfi_api.barchart.barchart_options.get_most_active_options()
    return {'data' : data}

@app.get("/options-change-in-open-interest")
async def change_in_open_interest(change_dir: Optional[str] = 'inc'):
    # TODO: initialise in fastapi startup event
    tradfi_api = await get_tradfi_api()
    data = await tradfi_api.barchart.barchart_options.get_change_in_options_interest(change_dir=change_dir)
    return {'data': data}

@app.get("/stocks/price/{symbol}")
async def stock_price(symbol: str, order='desc', interval='daily', num_records=20):
    MAX_RECORDS = 100

    if num_records > MAX_RECORDS:
        num_records = MAX_RECORDS
    # TODO: initialise in fastapi startup event
    tradfi_api = await get_tradfi_api()
    data = await tradfi_api.barchart.barchart_stocks.get_stock_prices(symbol=symbol, interval=interval, max_records=num_records, order=order)

    # format string response into json
    data['data'] = data.rstrip()
    formatted_prices = list(map(format_stock_price_object, data['data'].split('\n')))
    data['data'] = formatted_prices

    return {'data': data}

# TODO: Refactor
def format_stock_price_object(item):
    (symbol, date, open, high, low, close, volume) = item.split(',')
    return {
        'symbol': symbol,
        'date': date,
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }