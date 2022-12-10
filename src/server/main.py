from datetime import date
from fastapi import FastAPI
from typing import Optional

from barchart_api import BarChartAPI

import subprocess
import os
import asyncio

app = FastAPI()

options_api = BarChartAPI().options

async def run_migration():
    print('Running postgres migration scripts. Wait 5 seconds for timescale db to be ready')
    await asyncio.sleep(5)
    result = subprocess.run('piccolo migrations forwards market_data_piccolo --trace', cwd=os.getcwd(), timeout=30,
                            shell=True, capture_output=True)
    print(result)
    print(f'stdout: {result.stdout}')
    if result.stderr:
        print(f'stderr: {result.stderr}')

@app.on_event("startup")
async def startup_event():
    print('FastAPI startup event')
    await run_migration()

@app.get("/healthz")
async def health_check():
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