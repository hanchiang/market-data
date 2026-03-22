from abc import ABC, abstractmethod
from typing import Optional

from market_data_library.core.tradfi.api import BarchartAPI
from market_data_library.core.tradfi.barchart.stocks.stocks import StocksService

from market_data_piccolo.tables.stock_ticker import StockTicker


class BaseScraper(ABC):
    symbols_to_scrape = []

    def __init__(self):
        self.stocks_api: Optional[StocksService] = None

    @abstractmethod
    async def run(self):
        pass

    async def init_symbols_to_scrape(self):
        if len(self.symbols_to_scrape) > 0:
            return

        res = await StockTicker.select(StockTicker.symbol)
        self.symbols_to_scrape = list(map(lambda r: r['symbol'], res))
        return

    def get_stocks_api(self) -> StocksService:
        if self.stocks_api is None:
            self.stocks_api = BarchartAPI().barchart_stocks
        return self.stocks_api

    async def cleanup_stocks_api(self) -> None:
        if self.stocks_api is not None:
            await self.stocks_api.cleanup()
            self.stocks_api = None
