from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import datetime

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

    def transform_fields(self, uncameled_option_data, tz):
        """
        Transforms and validates specific fields in the given option data dictionary.

        This method processes the 'trade_time' and 'expiration_date' fields in the input dictionary:
        - Converts 'trade_time' from a timestamp to a timezone-aware datetime object.
        - Validates and converts 'expiration_date' from a string in 'YYYY-MM-DD' format to a datetime.date object.

        Args:
            uncameled_option_data (dict): A dictionary containing option data with fields 'trade_time' and 'expiration_date'.
            tz (datetime.tzinfo): The timezone information to use for converting 'trade_time'.

        Returns:
            dict or None: The updated dictionary with transformed fields if successful, or None if an error occurs.

        Raises:
            None: Any exceptions encountered during processing are caught and logged, and the method returns None.

        Notes:
            - If 'trade_time' is less than or equal to 0, it defaults to the Unix epoch (1970-01-01 00:00:00 UTC).
            - If 'expiration_date' is invalid, the method logs the error and returns None.
        """
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

    def prepare_expiration_dates_list(self, expiration_dates_res: barchart_type.OptionsExpiration) -> List[Dict[str, str]]:
        return [
            {
                'expiration_type': 'weekly',
                'expiration_dates': expiration_dates_res.weekly
            },
            {
                'expiration_type': 'monthly',
                'expiration_dates': expiration_dates_res.monthly
            }
        ]

    def get_rate_limit_info_from_response(self, res):
        return [int(res['rate_limit']['limit']), int(res['rate_limit']['remaining'])]

    async def get_expiration_dates(self, symbol: str) -> Tuple[List[str], List[str]]:
        res = await options_api.get_options_expirations_for_ticker(symbol=symbol)
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
