import asyncio
import datetime
import math
from typing import Tuple, List, Dict

from barchart_api import BarChartAPI
import time
import pytz

from src.job.scrape_util import random_sleep, get_year_month_day_from_yyyy_mm_dd, uncamel_case_dict, \
    stop_postgres_connection_pool, start_postgres_connection_pool
from market_data_piccolo.tables import OptionPrice

options_api = BarChartAPI().options

class Result:
    def __init__(self):
        self.symbol_fetched_count = {}

    def get_symbol_fetched_count(self):
        return self.symbol_fetched_count

    def get_fetched_count_for_symbol(self, symbol: str):
        return self.symbol_fetched_count.get(symbol, None)

    def set_fetched_count_for_symbol(self, symbol: str, value: int):
        self.symbol_fetched_count[symbol] = value

    def increase_fetched_count_for_symbol_by(self, symbol: str, delta: int):
        self.symbol_fetched_count[symbol] += delta

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
        expected_requests = elapsed_seconds * self.request_limit_per_sec

        if requests_used <= expected_requests or self.remaining > self.limit / 2:
            return

        actual_requests_rate = requests_used / elapsed_seconds
        duration_to_sleep = (actual_requests_rate - self.request_limit_per_sec) * elapsed_seconds
        duration_to_sleep = max(0, math.ceil(duration_to_sleep))
        if duration_to_sleep > 0:
            print(
                f'Enforcing rate limit. Time elapsed {elapsed_seconds} seconds, requests used {requests_used}, expected requests {expected_requests}, duration to sleep {duration_to_sleep} seconds')
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

class Scraper:
    async def run(self):
        symbols = ['SPY', 'QQQ', 'DIA']
        now = datetime.datetime.now()
        ny_tz = pytz.timezone('America/New_York')
        ny_now = now.astimezone(tz=ny_tz)
        start_time = time.time()

        # Get the latest trading day in NY timezone
        # Adjust for weekends
        # TODO: Account for holidays?
        # 0 = monday, 6 = sunday
        default_trade_time = ny_now
        if ny_now.weekday() >= 5:
            days_to_deduct = ny_now.weekday() - 4
            default_trade_time = default_trade_time - datetime.timedelta(days=days_to_deduct)
        # Check whether market has opened
        if default_trade_time.hour < 9 or (default_trade_time.hour == 9 and default_trade_time.minute < 30):
            default_trade_time = default_trade_time - datetime.timedelta(days=1)

        # market hours: 9.30am - 4pm
        default_trade_time = default_trade_time.replace(hour=9, minute=30, second=0, microsecond=0)
        print(f'default trade time: {default_trade_time}')

        await start_postgres_connection_pool()

        result = Result()
        rate_limiter = RateLimit()

        for symbol in symbols:
            await self.scrape_ticker(symbol=symbol, tz=ny_tz, result=result, rate_limiter=rate_limiter)
            print('\n')

        for k, v in result.get_symbol_fetched_count().items():
            print(f'Fetched {v} results for {k}')

        await stop_postgres_connection_pool()

        end_time = time.time()
        print(f'Took {end_time - start_time} seconds')

    async def scrape_ticker(self, symbol: str, tz, result: Result, rate_limiter: RateLimit):
        start_time = time.time()
        print(f'Fetching options data for {symbol}')

        if result.get_fetched_count_for_symbol(symbol) is None:
            result.set_fetched_count_for_symbol(symbol, 0)

        expiration_dates_res = await self.get_expiration_dates(symbol)
        [rate_limit_limit, rate_limit_remaining] = self.get_rate_limit_info_from_response(expiration_dates_res)
        await rate_limiter.handle_rate_limit(rate_limit_limit, rate_limit_remaining)
        weekly_monthly_expirations = self.prepare_expiration_dates_list(expiration_dates_res)

        for expiration in weekly_monthly_expirations:
            for ex_date in expiration['expiration_dates']:
                print(f'Getting options data for {expiration["expiration_type"]} {ex_date}')
                options_res = await self.get_options_data(symbol=symbol, expiration_date=ex_date,
                                                          expiration_type=expiration['expiration_type'])
                print(f'Fetched {options_res["count"]} results')
                result.increase_fetched_count_for_symbol_by(symbol, options_res['count'])
                [rate_limit_limit, rate_limit_remaining] = self.get_rate_limit_info_from_response(options_res)
                await rate_limiter.handle_rate_limit(rate_limit_limit, rate_limit_remaining)

                # insert into option_price table
                option_price_to_insert = []
                for option_data in options_res['data']:
                    uncameled_option_data = uncamel_case_dict(option_data)['raw']
                    # transform fields
                    if self.transform_fields(uncameled_option_data, tz=tz) is None:
                        print(f'transformed fields failed, skipping {uncameled_option_data}')
                        continue
                    option_price = OptionPrice(uncameled_option_data)
                    option_price_to_insert.append(OptionPrice.insert(option_price))
                try:
                    if len(option_price_to_insert) > 0:
                        print(f'Inserting {len(option_price_to_insert)} option price')
                        await asyncio.gather(*option_price_to_insert)
                except Exception as e:
                    print(e)
                await random_sleep()

        end_time = time.time()
        return f'{symbol} took {end_time - start_time} seconds'

    def transform_fields(self, uncameled_option_data, tz):
        try:
            trade_time = uncameled_option_data['trade_time']
            uncameled_option_data['trade_time'] = datetime.datetime.fromtimestamp(trade_time, tz=tz) if trade_time > 0 else datetime.datetime.fromtimestamp(0)
        except Exception as e:
            print(f'Encountered error when setting trade_time, {e}')
            return None
        expiration_date_year, expiration_date_month, expiration_date_day = get_year_month_day_from_yyyy_mm_dd(uncameled_option_data['expiration_date'])
        try:
            datetime.date(int(expiration_date_year), int(expiration_date_month), int(expiration_date_day))
            uncameled_option_data['expiration_date'] = datetime.date(int(expiration_date_year),
                                                                     int(expiration_date_month),
                                                                     int(expiration_date_day))
        except Exception as e:
            print(f'Encountered error when setting expiration_date, {e}')
            return None

        return uncameled_option_data

    async def get_expiration_dates(self, symbol: str) -> Tuple[List[str], List[str]]:
        res = await options_api.get_options_expirations_for_ticker(symbol=symbol)
        return res

    async def get_options_data(self, symbol: str, expiration_date: str, expiration_type: str):
        # TODO: pass in fields?
        fields = ["symbol,baseSymbol,strikePrice,moneyness,bidPrice,midpoint,askPrice,lastPrice,priceChange,percentChange,volume,openInterest,volumeOpenInterestRatio,volatility,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,historicVolatility30d,baseNextEarningsDate,expirationType,delta,theta,gamma,vega,rho"]
        res = await options_api.get_options_for_ticker(symbol=symbol, expiration_date=expiration_date, expiration_type=expiration_type, order_by='tradeTime', order_dir='desc')

        if res['count'] < res['total']:
            print('Count is less than total. This means that not all results are fetched. Please use a more stringent search criteria to reduce the result set')

        return res

    def prepare_expiration_dates_list(self, expiration_dates_res) -> List[Dict[str, str]]:
        expirations = expiration_dates_res['meta']['expirations']
        return [
            {
                'expiration_type': 'weekly',
                'expiration_dates': expirations['weekly']
            },
            {
                'expiration_type': 'monthly',
                'expiration_dates': expirations['monthly']
            }
        ]

    def get_rate_limit_info_from_response(self, res):
        return [int(res['rate_limit']['limit']), int(res['rate_limit']['remaining'])]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    scraper = Scraper()
    loop.run_until_complete(scraper.run())