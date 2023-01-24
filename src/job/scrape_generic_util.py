import asyncio
import multiprocessing
import re
import random
from typing import Any, Dict

from piccolo.engine import engine_finder

# camelCase -> camel_case
def uncamel_case(input: str) -> str:
    if len(input) == 0:
        return ''

    result = [input[0].lower()]
    uppercase_regex = re.compile('[A-Z]')
    for c in input[1:]:
        if uppercase_regex.match(c) is not None:
            result.append('_')
            result.append(c.lower())
        else:
            result.append(c)
    return ''.join(result)

def uncamel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    uncamel_case_dict_inner(d, result)
    return result

def uncamel_case_dict_inner(d: Dict[str, Any], result: Dict[str, Any]):
    for k, v in d.items():
        if type(v) is not dict:
            result[uncamel_case(k)] = v
        else:
            result[uncamel_case(k)] = {}
            uncamel_case_dict_inner(v, result[uncamel_case(k)])

async def random_sleep(min_second = 0.1):
    sleep_duration = random.uniform(min_second, min_second + 1)
    print(f'Sleeping for {sleep_duration} seconds')
    await asyncio.sleep(sleep_duration)

async def start_postgres_connection_pool():
    engine = engine_finder()
    await engine.start_connection_pool(min_size=multiprocessing.cpu_count()/2, max_size=multiprocessing.cpu_count())

async def stop_postgres_connection_pool():
    engine = engine_finder()
    await engine.close_connection_pool()

# 2022-12-03
def get_year_month_day_from_yyyy_mm_dd(d):
    return [d[0:4], d[5:7], d[8:10]]