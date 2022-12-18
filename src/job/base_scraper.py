import asyncio
from abc import ABC, abstractmethod
import datetime
from typing import Tuple, List, Dict

from barchart_api import BarChartAPI
import time

from src.job.scrape_helper_class import Result, RateLimit
from src.job.scrape_generic_util import random_sleep, get_year_month_day_from_yyyy_mm_dd, uncamel_case_dict
from market_data_piccolo.tables import OptionPrice

options_api = BarChartAPI().options

class BaseScraper(ABC):
    symbols = ['SPY', 'QQQ', 'DIA', 'TSLA', 'AAPL', 'AMZN', 'NVDA', 'BABA', 'AMD', 'NFLX', 'GOOG', 'MSFT', 'MSFT',
               'AMC', 'COIN', 'TLT']

    def __init__(self, result: Result, rate_limiter: RateLimit):
        self.result = result
        self.rate_limiter = rate_limiter

    @abstractmethod
    async def run(self):
        pass

    def report(self, result: Result):
        fetch_count = 0
        fetch_time = 0

        for k, v in result.get_symbol_fetch_count().items():
            print(f'Fetched {v} results for {k}')
            fetch_count += v
        print(f'Fetched {fetch_count} results in total')
        for k, v in result.get_symbol_fetch_time().items():
            print(f'{k} took {v} seconds')
            fetch_time += v
        print(f'Took {fetch_time} seconds in total')

        print(f'Took {result.db_insert_time} seconds to insert into DB')

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
        res = await options_api.get_options_expirations_for_ticker(symbol=symbol)
        return res

    async def get_options_data(self, symbol: str, expiration_date: str, expiration_type: str):
        # TODO: pass in fields?
        fields = [
            "symbol,baseSymbol,strikePrice,moneyness,bidPrice,midpoint,askPrice,lastPrice,priceChange,percentChange,volume,openInterest,volumeOpenInterestRatio,volatility,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,historicVolatility30d,baseNextEarningsDate,expirationType,delta,theta,gamma,vega,rho"]
        res = await options_api.get_options_for_ticker(symbol=symbol, expiration_date=expiration_date,
                                                       expiration_type=expiration_type, order_by='tradeTime',
                                                       order_dir='desc')

        if res['count'] < res['total']:
            print(
                'Count is less than total. This means that not all results are fetched. Please use a more stringent search criteria to reduce the result set')

        return res