import asyncio
import datetime
import time
from typing import Any

from asyncio_tools import GatheredResults, gather
from zoneinfo import ZoneInfo

from market_data_piccolo.tables.option_price import OptionPrice
from src.job.options.base_scraper import BaseScraper, Result
from src.job.scrape_generic_util import (
    random_sleep,
    start_postgres_connection_pool,
    stop_postgres_connection_pool,
)
from src.market_data_library_adapter import (
    option_price_to_db_row,
    prepare_expiration_batches,
)
from src.utils.date_util import get_most_recent_trading_day

ny_tz = ZoneInfo("America/New_York")


def get_default_trade_time(
    reference_datetime: datetime.datetime | None = None,
) -> datetime.datetime:
    """Return the canonical 9:30 a.m. NY trade-time anchor for this scraper."""
    return get_most_recent_trading_day(reference_datetime).replace(
        hour=9,
        minute=30,
        second=0,
        microsecond=0,
    )


class Scraper(BaseScraper):
    async def run(self):
        start_time = time.time()

        default_trade_time = get_default_trade_time()

        await start_postgres_connection_pool()
        try:
            await self.init_symbols_to_scrape()
            print(f'{len(self.symbols_to_scrape)} symbols to scrape: {self.symbols_to_scrape}, default trade time: {default_trade_time}')
            for symbol in self.symbols_to_scrape:
                try:
                    inserted = await self.scrape_ticker(
                        symbol=symbol,
                        tz=ny_tz,
                        default_trade_time=default_trade_time,
                    )
                    # TODO: post check
                    print(f"inserted data for {symbol} into DB?:", inserted)
                except Exception as e:
                    print(f"[run] error: {e}")
                    raise
                    # TODO: send telegram notification

            # TODO: send email/telegram notification
            print(self.result.get_report())
        finally:
            await self.cleanup_options_api()
            await stop_postgres_connection_pool()

        end_time = time.time()
        print(f'Took {end_time - start_time} seconds')

    async def scrape_ticker(
        self,
        symbol: str,
        tz: Any,
        default_trade_time: datetime.datetime,
    ) -> bool:
        # TODO: should probably ignore strike prices that are more than a certain number outside
        # of the current stock price(e.g. 20%)
        start_time = time.time()
        print(f'Fetching options data for {symbol}')

        if self.result.get_fetch_count_for_symbol(symbol) is None:
            self.result.set_fetch_count_for_symbol(symbol, 0)

        # Get expiration dates
        # TODO: if expirations is in the past and they are already in DB, skip it
        expiration_dates_res = await self.get_expiration_dates(symbol)
        weekly_monthly_expirations = prepare_expiration_batches(expiration_dates_res)

        # Get options data for each expiration date
        before_db_insert_count = self.result.db_insert_count
        for expiration in weekly_monthly_expirations:
            for ex_date in expiration['expiration_dates']:
                option_price_to_insert = []
                print(f'Getting options data for {expiration["expiration_type"]} {ex_date}')
                # TODO: should probably ignore strike prices that are more than a certain number outside of the current stock price(e.g. 20%)
                # TODO: Skip those options where trade_time < (latest trade_time saved for the base_symbol in DB) - 1 day
                options_res = await self.get_options_data(symbol=symbol, expiration_date=ex_date,
                                                          expiration_type=expiration['expiration_type'])
                fetch_count = len(options_res)
                print(f'Fetched {fetch_count} results')
                self.result.increase_fetch_count_for_symbol(symbol, fetch_count)

                for option_data in options_res:
                    option_price = OptionPrice(
                        option_price_to_db_row(
                            option_data,
                            tz=tz,
                            default_trade_time=default_trade_time,
                        )
                    )
                    option_price_to_insert.append(OptionPrice.insert(option_price))
                try:
                    if len(option_price_to_insert) > 0:
                        print(f'Inserting {len(option_price_to_insert)} option price')
                        before_insert_db = time.time()
                        gathered_result: GatheredResults = await gather(*option_price_to_insert)
                        self.result.increase_db_insert_time(time.time() - before_insert_db)
                        self.result.increase_db_insert_count(gathered_result.success_count)
                        if gathered_result.exception_count > 0:
                            print(f'[scrape_ticker] There are {gathered_result.exception_count} insert DB errors:', gathered_result.exceptions)
                except Exception as e:
                    print(f'[scrape_ticker] error: {e}')
                    raise RuntimeError(e) from e
                await random_sleep(0.1)
            await random_sleep(1)
        await random_sleep(3)
        end_time = time.time()
        self.result.set_symbol_fetch_time_for_symbol(symbol, end_time - start_time)
        return True if self.result.db_insert_count > before_db_insert_count else False


async def main():
    scraper = Scraper(result=Result())
    await scraper.run()

# python src/job/options/scraper.py
# TODO: try threadpool: https://stackoverflow.com/questions/31623194/asyncio-two-loops-for-different-i-o-tasks/62631135#62631135
if __name__ == '__main__':
    asyncio.run(main())
