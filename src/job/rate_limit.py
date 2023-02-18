import asyncio
import math
import time


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