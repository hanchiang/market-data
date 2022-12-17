from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table
from market_data_piccolo.tables import StockTickerPrice, OptionPrice, StockTicker

ID = "2022-12-04T14:58:26:086283"
VERSION = "0.99.0"
DESCRIPTION = "Create tables"

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

# dummy table to execute raw SQL
class RawTable(Table):
    pass

# For some reason, creating tables with pure SQL result in the piccolo table having only an id column...
async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="market_data_piccolo", description=DESCRIPTION
    )
    async def create_stock_ticker():
        print(await StockTicker.create_table())

    async def create_stock_ticker_price():
        await StockTickerPrice.create_table()
        # HACK: remove default id primary key, then recreate primary key with id and date
        # 1. Because piccolo forces us to create a primary key
        # 2. However any primary key or unique index in timescale db needs to include the partition column(date)
        await RawTable.raw('ALTER TABLE stock_ticker_price DROP CONSTRAINT stock_ticker_price_pkey;')
        await RawTable.raw('ALTER TABLE stock_ticker_price ADD PRIMARY KEY (id, date);')

        await RawTable.raw("CREATE UNIQUE INDEX stock_ticker_price_sym_date_uq ON stock_ticker_price(symbol, date);")
        print(await RawTable.raw("SELECT create_hypertable('stock_ticker_price', 'date');"))

    async def create_option_price():
        await OptionPrice.create_table()

        # HACK: remove default id primary key, then recreate primary key with id and date
        # 1. Because piccolo forces us to create a primary key
        # 2. However any primary key or unique index in timescale db needs to include the partition column(trade_time)
        await RawTable.raw('ALTER TABLE option_price DROP CONSTRAINT option_price_pkey;')
        await RawTable.raw('ALTER TABLE option_price ADD PRIMARY KEY (id, trade_time);')

        await RawTable.raw(
            "CREATE UNIQUE INDEX option_price_sym_tradetime_exdate_strike_opt_type_uq ON option_price(symbol, trade_time, expiration_date, strike_price, option_type);")
        print(await RawTable.raw("SELECT create_hypertable('option_price', 'trade_time')"))

    async def run():
        await create_stock_ticker()
        await create_stock_ticker_price()
        await create_option_price()

    async def run_backwards():
        await RawTable.raw('DROP TABLE option_price')
        await RawTable.raw('DROP TABLE stock_ticker_price')
        await RawTable.raw('DROP TABLE stock_ticker')

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
