import asyncio
import math
import time


class Result:
    def __init__(self):
        self.symbol_fetch_count = {}
        self.symbol_fetch_time_seconds = {}
        self.fetch_count = 0
        self.fetch_time = 0
        self.db_insert_time = 0

    def get_fetch_count_for_symbol(self, symbol: str):
        return self.symbol_fetch_count.get(symbol, None)

    def set_fetch_count_for_symbol(self, symbol: str, value: int):
        self.symbol_fetch_count[symbol] = value

    def increase_fetch_count_for_symbol(self, symbol: str, delta: int):
        self.symbol_fetch_count[symbol] += delta

    def get_symbol_fetch_time_for_symbol(self, symbol: str):
        return self.symbol_fetch_time_seconds.get(symbol, None)

    def set_symbol_fetch_time_for_symbol(self, symbol: str, time_taken: int):
        self.symbol_fetch_time_seconds[symbol] = time_taken

    def increase_db_insert_time(self, delta: int):
        self.db_insert_time += delta

    def sort(self):
        self.symbol_fetch_count = { k: v for k, v in sorted(self.symbol_fetch_count.items(), key=lambda x: x[1], reverse=True) }
        self.symbol_fetch_time_seconds = { k: v for k, v in sorted(self.symbol_fetch_time_seconds.items(), key=lambda x: x[1], reverse=True) }
    def report(self):
        self.sort()

        if len(self.symbol_fetch_count) != len(self.symbol_fetch_time_seconds):
            print(f'symbol_fetch_count and symbol_fetch_time_seconds dont have the same number of symbols')

        for symbol, count in self.symbol_fetch_count.items():
            self.fetch_count += count
            fetch_time = self.symbol_fetch_time_seconds[symbol]
            self.fetch_time += fetch_time

            print(f'Retrieved {count} results for {symbol}, time taken: {fetch_time} seconds, average time per item: {fetch_time / count} seconds')

        print(f'Retrieved {self.fetch_count} results for {len(self.symbol_fetch_count)} symbols, time taken: {self.fetch_time} seconds, average time per item: {self.fetch_time / self.fetch_count} seconds')
        print(f'Took {self.db_insert_time} seconds to insert {self.fetch_count} rows into DB, average time per row: {self.db_insert_time / self.fetch_count}')

# TODO: test
class RateLimit:
    request_limit_per_sec = 1

    def __init__(self):
        self.start_time = None
        # per minute
        self.limit = None
        self.prev_remaining = None
        self.remaining = None

    def has_initialised_limit_and_remaining(self) -> bool:
        return self.limit is not None and self.remaining is not None

    async def check_and_sleep(self):
        elapsed_seconds = time.time() - self.start_time
        requests_used = self.limit - self.remaining
        maximum_requests = elapsed_seconds * self.request_limit_per_sec

        if requests_used <= maximum_requests or self.remaining > self.limit / 2:
            return

        actual_requests_rate = requests_used / elapsed_seconds
        duration_to_sleep = (actual_requests_rate - self.request_limit_per_sec) * elapsed_seconds
        duration_to_sleep = max(0, math.ceil(duration_to_sleep))
        if duration_to_sleep > 0:
            print(
                f'Enforcing rate limit. Time elapsed {elapsed_seconds} seconds, requests used {requests_used}, maximum requests {maximum_requests}, duration to sleep {duration_to_sleep} seconds')
            await asyncio.sleep(duration_to_sleep)


    # 60 requests per minute, for all endpoints
    async def handle_rate_limit(self, new_limit: int, new_remaining: int):
        if not self.has_initialised_limit_and_remaining():
            self.limit = new_limit
            self.remaining = new_remaining
            self.start_time = time.time()
            print(f'Initialising rate limit, limit {self.limit}, remaining: {self.remaining}')
            return

        print(f'rate limit! limit: {new_limit}, remaining: {new_remaining}')

        # new_limit should be the same as self.limit
        if self.limit != new_limit:
            print(f'New limit {new_limit} is different from self.limit {self.limit}')

        # rate limit is refreshed
        if new_remaining > self.remaining:
            self.prev_remaining = None
            self.start_time = time.time()
            print(f'Rate limit is refreshed')
        else:
            self.prev_remaining = self.remaining
        self.remaining = new_remaining

        await self.check_and_sleep()