from datetime import date
from fastapi import FastAPI
from typing import Optional

from barchart_api import BarChartAPI

from src.db.index import run_migration, start_postgres_connection_pool, stop_postgres_connection_pool

app = FastAPI()

options_api = BarChartAPI().options

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

# TODO: Use an arg to determine whether to connect to API source or DB
@app.get("/options/{symbol}")
async def options_for_ticker(
    symbol: str, order_dir = '', expiration_type = '', expiration_date: Optional[date] = None,
    group_by: Optional[str] = '', order_by: Optional[str] = ''
):
    data = await options_api.get_options_for_ticker(symbol=symbol, expiration_type=expiration_type,
        expiration_date=expiration_date, group_by=group_by, order_by=order_by, order_dir=order_dir
    )

    return {'data': data}

@app.get("/options/{symbol}/expirations")
async def options_expirations_for_ticker(symbol: str):
    # TODO: cache
    data = await options_api.get_options_expirations_for_ticker(symbol=symbol)
    return {'data': data}