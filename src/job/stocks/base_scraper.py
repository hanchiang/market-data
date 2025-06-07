from abc import ABC, abstractmethod


from market_data_piccolo.tables.stock_ticker import StockTicker


class BaseScraper(ABC):
    symbols_to_scrape = []

    def __init__(self):
        pass

    @abstractmethod
    async def run(self):
        pass

    async def init_symbols_to_scrape(self):
        if len(self.symbols_to_scrape) > 0:
            return

        res = await StockTicker.select(StockTicker.symbol)
        self.symbols_to_scrape = list(map(lambda r: r['symbol'], res))
        return

    def get_rate_limit_info_from_response(self, res):
        return [int(res['rate_limit']['limit']), int(res['rate_limit']['remaining'])]
