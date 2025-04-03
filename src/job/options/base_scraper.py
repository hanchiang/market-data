from abc import ABC, abstractmethod
import datetime
from typing import Tuple, List, Dict

from src.job.options.scrape_helper_class import Result
from src.job.scrape_generic_util import get_year_month_day_from_yyyy_mm_dd
from market_data_piccolo.tables.stock_ticker import StockTicker
from src.data_source.barchart import get_tradfi_api

class BaseScraper(ABC):
    symbols_to_scrape = []

    def __init__(self, result: Result):
        self.result = result

    @abstractmethod
    async def run(self):
        pass

    async def init_symbols_to_scrape(self):
        if len(self.symbols_to_scrape) > 0:
            return

        res = await StockTicker.select(StockTicker.symbol)
        self.symbols_to_scrape = list(map(lambda r: r['symbol'], res))
        return

    def print_report(self):
        print(self.result.get_report())

    def get_report(self):
        return self.result.get_report()

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

    async def get_expiration_dates(self, symbol: str) -> Tuple[List[str], List[str]]:
        # TODO: init tradfi_api once only
        tradfi_api = await get_tradfi_api()
        res = await tradfi_api.barchart.barchart_options.get_options_expirations_for_ticker(symbol=symbol)
        return res

    async def get_options_data(self, symbol: str, expiration_date: str, expiration_type: str):
        # TODO: pass in fields?
        tradfi_api = await get_tradfi_api()
        fields = [
            "symbol,baseSymbol,strikePrice,moneyness,bidPrice,midpoint,askPrice,lastPrice,priceChange,percentChange,volume,openInterest,volumeOpenInterestRatio,volatility,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,historicVolatility30d,baseNextEarningsDate,expirationType,delta,theta,gamma,vega,rho"]
        res = await tradfi_api.barchart.barchart_options.get_options_for_ticker(symbol=symbol, expiration_date=expiration_date,
                                                       expiration_type=expiration_type, order_by='tradeTime',
                                                       order_dir='desc')

        if res['count'] < res['total']:
            print(
                'Count is less than total. This means that not all results are fetched. Please use a more stringent search criteria to reduce the result set')

        return res