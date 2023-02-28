import asyncio
import math
import time


class Result:
    def __init__(self):
        self.symbol_fetch_count = {}
        self.symbol_fetch_time_seconds = {} # seconds
        self.fetch_count = 0
        self.fetch_time = 0
        self.db_insert_time = 0 # seconds
        self.db_insert_count = 0

    def get_fetch_count_for_symbol(self, symbol: str):
        return self.symbol_fetch_count.get(symbol, None)

    def set_fetch_count_for_symbol(self, symbol: str, value: int):
        self.symbol_fetch_count[symbol] = value

    def increase_fetch_count_for_symbol(self, symbol: str, delta: int):
        self.symbol_fetch_count[symbol] += delta

    def get_symbol_fetch_time_for_symbol(self, symbol: str):
        return self.symbol_fetch_time_seconds.get(symbol, None)

    def set_symbol_fetch_time_for_symbol(self, symbol: str, time_taken: int):
        self.symbol_fetch_time_seconds[symbol] = time_taken

    def increase_db_insert_time(self, delta: int):
        self.db_insert_time += delta

    def increase_db_insert_count(self, delta: int):
        self.db_insert_count += delta

    def sort(self):
        self.symbol_fetch_count = { k: v for k, v in sorted(self.symbol_fetch_count.items(), key=lambda x: x[1], reverse=True) }
        self.symbol_fetch_time_seconds = { k: v for k, v in sorted(self.symbol_fetch_time_seconds.items(), key=lambda x: x[1], reverse=True) }
    def get_report(self) -> str:
        self.sort()
        report = ''

        if len(self.symbol_fetch_count) != len(self.symbol_fetch_time_seconds):
            report = f'symbol_fetch_count and symbol_fetch_time_seconds dont have the same number of symbols'

        for symbol, count in self.symbol_fetch_count.items():
            self.fetch_count += count
            fetch_time = self.symbol_fetch_time_seconds.get(symbol, 0)
            self.fetch_time += fetch_time

            report = f'{report}\nRetrieved {count} results for {symbol}, time taken: {fetch_time} seconds'
            if count > 0:
                report = f'{report}, average time per item: {fetch_time / count} seconds'

        report = f'{report}\nRetrieved {self.fetch_count} results for {len(self.symbol_fetch_count)} symbols, time taken: {self.fetch_time} seconds'
        if self.fetch_count > 0:
            report = f'{report}, average time per item: {self.fetch_time / self.fetch_count} seconds'

        report = f'{report}\nTook {self.db_insert_time} seconds to insert {self.db_insert_count} rows into DB'
        if self.db_insert_count > 0:
            report = f'{report}, average time per row: {self.db_insert_time / self.db_insert_count}'
        rows_not_inserted_into_db = self.fetch_count - self.db_insert_count
        if rows_not_inserted_into_db > 0:
            report = f'{report}, {rows_not_inserted_into_db} rows are not inserted into DB'
        return report