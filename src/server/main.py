from datetime import date
from fastapi import FastAPI
from typing import Optional

from barchart_api import BarChartAPI

app = FastAPI()

options_api = BarChartAPI().options

@app.get("/healthz")
async def options_for_ticker():
    return {'data': 'market data is running!'}

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
    data = await options_api.get_options_expirations_for_ticker(symbol=symbol)

    return {'data': data}