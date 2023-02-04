import asyncio
import datetime
from typing import List, Dict

from barchart_api import BarChartAPI
import time
import pytz

from market_data_piccolo.tables.option_price import OptionPrice
from src.job.options.base_scraper import BaseScraper, Result, RateLimit
from src.job.options.scrape_generic_util import stop_postgres_connection_pool, start_postgres_connection_pool, \
    uncamel_case_dict, random_sleep

options_api = BarChartAPI().options



class Scraper(BaseScraper):
    async def run(self):
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
        print(f'{len(self.symbols)} symbols to scrape, default trade time: {default_trade_time}')

        await start_postgres_connection_pool()

        for symbol in self.symbols:
            inserted = await self.scrape_ticker(symbol=symbol, tz=ny_tz)
            # TODO: post check
            print("inserted data into DB:", inserted)
            print('\n')

        self.report()

        await stop_postgres_connection_pool()

        end_time = time.time()
        print(f'Took {end_time - start_time} seconds')

    async def scrape_ticker(self, symbol: str, tz) -> List[Dict]:
        # TODO: Should check if symbol is in stock_ticker table first before proceeding
        start_time = time.time()
        print(f'Fetching options data for {symbol}')

        if self.result.get_fetch_count_for_symbol(symbol) is None:
            self.result.set_fetch_count_for_symbol(symbol, 0)

        expiration_dates_res = await self.get_expiration_dates(symbol)
        [rate_limit_limit, rate_limit_remaining] = self.get_rate_limit_info_from_response(expiration_dates_res)
        await self.rate_limiter.handle_rate_limit(rate_limit_limit, rate_limit_remaining)
        weekly_monthly_expirations = self.prepare_expiration_dates_list(expiration_dates_res)

        gathered_result = []
        for expiration in weekly_monthly_expirations:
            for ex_date in expiration['expiration_dates']:
                option_price_to_insert = []
                print(f'Getting options data for {expiration["expiration_type"]} {ex_date}')
                options_res = await self.get_options_data(symbol=symbol, expiration_date=ex_date,
                                                          expiration_type=expiration['expiration_type'])
                print(f'Fetched {options_res["count"]} results')
                self.result.increase_fetch_count_for_symbol(symbol, options_res['count'])
                [rate_limit_limit, rate_limit_remaining] = self.get_rate_limit_info_from_response(options_res)
                await self.rate_limiter.handle_rate_limit(rate_limit_limit, rate_limit_remaining)

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
                        before_insert_db = time.time()
                        gathered_result.extend(await asyncio.gather(*option_price_to_insert))
                        self.result.increase_db_insert_time(time.time() - before_insert_db)
                except Exception as e:
                    print("[scrape_ticker] error:", e)
                await random_sleep(0.1)
            await random_sleep(1)
        await random_sleep(3)
        end_time = time.time()
        self.result.set_symbol_fetch_time_for_symbol(symbol, end_time - start_time)
        return True if len(gathered_result) > 0 else False


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    scraper = Scraper(result=Result(), rate_limiter=RateLimit())
    loop.run_until_complete(scraper.run())