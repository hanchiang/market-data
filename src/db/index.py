import multiprocessing

from piccolo.engine import engine_finder

async def start_postgres_connection_pool():
    engine = engine_finder()
    min_size = max(1, multiprocessing.cpu_count() // 2)
    max_size = max(1, multiprocessing.cpu_count())
    await engine.start_connection_pool(min_size=min_size, max_size=max_size)

async def stop_postgres_connection_pool():
    engine = engine_finder()
    await engine.close_connection_pool()
