import asyncio
import datetime
from typing import List, Dict

import time
from zoneinfo import ZoneInfo
from asyncio_tools import gather, GatheredResults

from src.data_source.barchart import get_tradfi_api
from src.job.stocks.base_scraper import BaseScraper
from market_data_piccolo.tables.stock_ticker_price import StockTickerPrice
from src.job.scrape_generic_util import stop_postgres_connection_pool, start_postgres_connection_pool, random_sleep
from src.utils.date_util import get_most_recent_trading_day

ny_tz = ZoneInfo("America/New_York")

class Scraper(BaseScraper):
    async def run(self):
        now = datetime.datetime.now()
        ny_now = now.astimezone(tz=ny_tz)
        start_time = time.time()

        # Get the latest trading day in NY timezone
        most_recent_trade_day = get_most_recent_trading_day()

        await start_postgres_connection_pool()

        await self.init_symbols_to_scrape()
        print(f'{len(self.symbols_to_scrape)} symbols to scrape: {self.symbols_to_scrape}, trade day: {str(most_recent_trade_day)}')
        for symbol in self.symbols_to_scrape:
            try:
                inserted = await self.scrape_ticker(symbol=symbol)
                # TODO: post check
                print(f"inserted data for {symbol} into DB?:", inserted)
                await random_sleep(1)
            except Exception as e:
                print(f"[run] error: {e}")
                raise e
                # TODO: send telegram notification

        # TODO: send email/telegram notification
        # print(self.result.get_report())

        await stop_postgres_connection_pool()

        end_time = time.time()
        print(f'Took {end_time - start_time} seconds')

    async def scrape_ticker(self, symbol: str) -> List[Dict]:
        latest_stock_ticker_price = await StockTickerPrice.select(StockTickerPrice.date)\
            .where(StockTickerPrice.symbol == symbol)\
            .order_by(StockTickerPrice.date, ascending=False).limit(1).run()
        start_time = time.time()

        records_to_retrieve = None
        if latest_stock_ticker_price is not None and latest_stock_ticker_price[0] is not None:
            latest_stock_ticker_price_date: datetime.date = latest_stock_ticker_price[0]['date']
            most_recent_trade_day = get_most_recent_trading_day().date()
            delta = most_recent_trade_day - latest_stock_ticker_price_date
            records_to_retrieve = delta.days
            print(f"Latest stock ticker price date: {latest_stock_ticker_price_date}, most recent trade day: {most_recent_trade_day}, delta: {delta.days}")
            if records_to_retrieve == 0:
                print(f'No data to retrieve for {symbol}. Latest stock ticker price date: {latest_stock_ticker_price_date}, most recent trade day: {most_recent_trade_day}')
                return []
        else:
            print(f'Stock price for {symbol} has not been saved before. Getting all historical prices')
        print(f'Number of records to retrieve for {symbol}: {records_to_retrieve if records_to_retrieve else "all"}')

        tradfi_api = await get_tradfi_api()
        data = await tradfi_api.barchart.barchart_stocks.get_stock_prices(symbol=symbol, max_records=records_to_retrieve)

        stock_ticker_price_to_insert = []
        for stock_ticker_price in data:
            stock_ticker_price = StockTickerPrice(
                symbol=stock_ticker_price.symbol,
                date=stock_ticker_price.date,
                open_price=stock_ticker_price.open_price,
                high_price=stock_ticker_price.high_price,
                low_price=stock_ticker_price.low_price,
                close_price=stock_ticker_price.close_price,
                volume=stock_ticker_price.volume,
            )
            stock_ticker_price_to_insert.append(StockTickerPrice.insert(stock_ticker_price))
        try:
            gathered_result: GatheredResults = await gather(*stock_ticker_price_to_insert)
            if gathered_result.exception_count > 0:
                print(f'[scrape_ticker] There are {gathered_result.exception_count} insert DB errors:',
                      gathered_result.exceptions)
        except Exception as e:
            # TODO: DataError("invalid input for query argument $2: '2023-02-10' ('str' object has no attribute 'toordinal')"
            print('[scrape_ticker] error:', e)
            raise RuntimeError(e)

        end_time = time.time()
        print(f'Took {end_time - start_time} seconds to get stock price for {symbol}')
        return True if gathered_result.success_count > 0 else False



async def main():
    scraper = Scraper()
    await scraper.run()

# python src/job/stocks/scraper.py
if __name__ == '__main__':
    asyncio.run(main())