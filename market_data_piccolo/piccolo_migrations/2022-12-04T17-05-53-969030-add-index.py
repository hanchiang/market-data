from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2022-12-04T17:05:53:969030"
VERSION = "0.99.0"
DESCRIPTION = "Add index"

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

class RawTable(Table):
    pass

async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="market_data_piccolo", description=DESCRIPTION
    )

    async def create_stock_ticker_index():
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS stock_ticker_symbol
            ON stock_ticker USING btree
            (symbol ASC NULLS LAST);
            ''')

    async def create_stock_ticker_price_index():
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS stock_ticker_price_symbol_date
            ON stock_ticker_price USING btree
            (symbol ASC NULLS LAST, date ASC NULLS LAST);
            ''')

    async def create_option_price_index():
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS option_price_base_symbol
            ON option_price USING btree
            (base_symbol ASC NULLS LAST);
            ''')
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS option_price_base_symbol_expiration_date
            ON option_price USING btree
            (base_symbol ASC NULLS LAST, expiration_date ASC NULLS LAST);
            ''')
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS option_price_base_symbol_option_type
            ON option_price USING btree
            (base_symbol ASC NULLS LAST, option_type ASC NULLS LAST);
            ''')
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS option_price_base_symbol_strike_price
            ON option_price USING btree
            (base_symbol ASC NULLS LAST, strike_price ASC NULLS LAST);
            ''')
        await RawTable.raw('''
            CREATE INDEX IF NOT EXISTS option_price_base_symbol_trade_time
            ON option_price USING btree
            (base_symbol ASC NULLS LAST, trade_time ASC NULLS LAST);
            ''')

    async def delete_stock_ticker_index():
        await RawTable.raw('DROP INDEX IF EXISTS stock_ticker_symbol;')

    async def delete_stock_ticker_price_index():
        await RawTable.raw('DROP INDEX IF EXISTS stock_ticker_price_symbol_date;')

    async def delete_option_price_index():
        await RawTable.raw('DROP INDEX IF EXISTS option_price_base_symbol;')
        await RawTable.raw('DROP INDEX IF EXISTS option_price_base_symbol_expiration_date;')
        await RawTable.raw('DROP INDEX IF EXISTS option_price_base_symbol_option_type;')
        await RawTable.raw('DROP INDEX IF EXISTS option_price_base_symbol_strike_price;')
        await RawTable.raw('DROP INDEX IF EXISTS option_price_base_symbol_trade_time;')

    async def run():
        await create_stock_ticker_index()
        await create_stock_ticker_price_index()
        await create_option_price_index()

    async def run_backwards():
        await delete_stock_ticker_index()
        await delete_stock_ticker_price_index()
        await delete_option_price_index()

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
