from fastapi import FastAPI
from typing import Optional

from src.market_data_library_adapter import serialize_payload
from market_data_library.core.tradfi.api import BarchartAPI

from src.db.index import run_migration, start_postgres_connection_pool, stop_postgres_connection_pool

app = FastAPI()

barchart: Optional[BarchartAPI] = None


def get_barchart_api() -> BarchartAPI:
    if barchart is None:
        raise RuntimeError("Barchart API is not initialized")
    return barchart

@app.on_event("startup")
async def startup_event():
    global barchart
    print('FastAPI startup event')
    barchart = BarchartAPI()
    await start_postgres_connection_pool()
    await run_migration()

@app.on_event('shutdown')
async def shutdown_event():
    global barchart
    print('FastAPI shutdown event')
    await stop_postgres_connection_pool()
    if barchart is not None:
        await barchart.barchart_stocks.cleanup()
        await barchart.barchart_options.cleanup()
        barchart = None

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
    data = await get_barchart_api().barchart_options.get_options_for_ticker(symbol=symbol, expiration_type=expiration_type,
        expiration_date=expiration_date, group_by=group_by, order_by=order_by, order_dir=order_dir
    )

    return {'data': serialize_payload(data)}

@app.get("/options/{symbol}/expirations")
async def options_expirations_for_ticker(symbol: str):
    # TODO: cache
    data = await get_barchart_api().barchart_options.get_options_expirations_for_ticker(symbol=symbol)
    return {'data': serialize_payload(data)}

@app.get("/options-most-active")
async def most_active_options():
    data = await get_barchart_api().barchart_options.get_most_active_options()
    return {'data': serialize_payload(data)}

@app.get("/options-change-in-open-interest")
async def change_in_open_interest(change_dir: Optional[str] = 'inc'):
    data = await get_barchart_api().barchart_options.get_change_in_options_interest(change_dir=change_dir)
    return {'data': serialize_payload(data)}

@app.get("/stocks/price/{symbol}")
async def stock_price(symbol: str, order='desc', interval='daily', num_records=20):
    MAX_RECORDS = 100
    if num_records > MAX_RECORDS:
        num_records = MAX_RECORDS
    data = await get_barchart_api().barchart_stocks.get_stock_prices(symbol=symbol, interval=interval, max_records=num_records, order=order)
    return {'data': serialize_payload(data)}
