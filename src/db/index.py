import asyncio
import multiprocessing
import os
import subprocess

from piccolo.engine import engine_finder

async def run_migration():
    print('Running postgres migration scripts. Wait 1 seconds for timescale db to be ready')
    await asyncio.sleep(1)
    result = subprocess.run('piccolo migrations forwards market_data_piccolo --trace', cwd=os.getcwd(), timeout=60,
                            shell=True, capture_output=True)
    print(result)
    print(f'stdout: {result.stdout}')
    if result.stderr:
        print(f'stderr: {result.stderr}')

async def start_postgres_connection_pool():
    engine = engine_finder()
    await engine.start_connection_pool(min_size=multiprocessing.cpu_count()/2, max_size=multiprocessing.cpu_count())

async def stop_postgres_connection_pool():
    engine = engine_finder()
    await engine.close_connection_pool()