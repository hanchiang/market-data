from abc import ABC, abstractmethod
from typing import Optional

from market_data_library.core.tradfi.api import BarchartAPI
from market_data_library.core.tradfi.barchart.options.options import OptionService
from market_data_library.core.tradfi.barchart.type.barchart_type import (
    OptionsExpiration,
    OptionsPrice,
)

from src.job.options.option_price.scrape_helper_class import Result
from market_data_piccolo.tables.stock_ticker import StockTicker

class BaseScraper(ABC):
    symbols_to_scrape = []

    def __init__(self, result: Result):
        self.result = result
        self.options_api: Optional[OptionService] = None

    @abstractmethod
    async def run(self):
        pass

    async def init_symbols_to_scrape(self):
        if len(self.symbols_to_scrape) > 0:
            return

        res = await StockTicker.select(StockTicker.symbol)
        self.symbols_to_scrape = list(map(lambda r: r['symbol'], res))
        return

    def get_options_api(self) -> OptionService:
        if self.options_api is None:
            self.options_api = BarchartAPI().barchart_options
        return self.options_api

    async def cleanup_options_api(self) -> None:
        if self.options_api is not None:
            await self.options_api.cleanup()
            self.options_api = None

    def print_report(self):
        print(self.result.get_report())

    def get_report(self):
        return self.result.get_report()

    async def get_expiration_dates(self, symbol: str) -> OptionsExpiration:
        res = await self.get_options_api().get_options_expirations_for_ticker(symbol=symbol)
        return res

    async def get_options_data(
        self, symbol: str, expiration_date: str, expiration_type: str
    ) -> list[OptionsPrice]:
        return await self.get_options_api().get_options_for_ticker(
            symbol=symbol,
            expiration_date=expiration_date,
            expiration_type=expiration_type,
            order_by='tradeTime',
            order_dir='desc',
        )
