import datetime

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns import Varchar, BigSerial, ForeignKey, OnDelete, OnUpdate, Date, Numeric, Integer, Timestamptz
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table

ID = "2022-12-04T14:58:26:086283"
VERSION = "0.99.0"
DESCRIPTION = "Create tables"

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

class StockTicker(Table, tablename="stock_ticker"):
    id = BigSerial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name="id",
        secret=False,
    )
    symbol = Varchar(
        length=10,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    name = Varchar(
        length=255,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    created_at = Timestamptz(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False
    )

class StockTickerPrice(Table, tablename="stock_ticker_price"):
    id = BigSerial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name="id",
        secret=False,
    )
    symbol = ForeignKey(
        references=StockTicker,
        on_delete=OnDelete.no_action,
        on_update=OnUpdate.cascade,
        target_column='symbol',
        null=True,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    date = Date(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    open_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    high_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    low_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    close_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    volume = Integer(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    created_at = Timestamptz(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False
    )

class OptionPrice(Table, tablename="option_price"):
    id = BigSerial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name="id",
        secret=False,
    )
    symbol = Varchar(
        length=100,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    base_symbol = ForeignKey(
        references=StockTicker,
        on_delete=OnDelete.no_action,
        on_update=OnUpdate.cascade,
        target_column='symbol',
        null=True,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    trade_time = Timestamptz(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    option_type = Varchar(
        length=4,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    strike_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    open_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    high_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    low_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    last_price = Numeric(
        digits=stock_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    moneyness = Numeric(
        digits=option_aggregate_stat_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    bid_price = Numeric(
        digits=option_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    midpoint = Numeric(
        digits=option_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    ask_price = Numeric(
        digits=option_price_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    volume = Integer(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    open_interest = Integer(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    volatility = Numeric(
        digits=option_aggregate_stat_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    expiration_date = Date(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    expiration_type = Varchar(
        length=7,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    average_volatility = Numeric(
        digits=option_aggregate_stat_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    delta = Numeric(
        digits=option_greek_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    theta = Numeric(
        digits=option_greek_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    gamma = Numeric(
        digits=option_greek_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    vega = Numeric(
        digits=option_greek_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    rho = Numeric(
        digits=option_greek_precision,
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False,
    )
    created_at = Timestamptz(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False
    )


# dummy table to execute raw SQL
class RawTable(Table):
    pass

# TODO: Copy the table definition here. This is to make sure migrations are always deterministic

# For some reason, creating tables with pure SQL result in the piccolo table having only an id column...
async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="market_data_piccolo", description=DESCRIPTION
    )
    async def create_stock_ticker_table():
        await StockTicker.create_table()
        await RawTable.raw('''CREATE UNIQUE INDEX IF NOT EXISTS stock_ticker_symbol_uq
            ON stock_ticker USING btree
            (symbol ASC NULLS LAST);
            ''')

    async def create_stock_ticker_price_hypertable():
        await StockTickerPrice.create_table()
        # HACK: remove default id primary key, then recreate primary key with id and date
        # 1. Because piccolo forces us to create a primary key
        # 2. However any primary key or unique index in timescale db needs to include the partition column(date)
        # https://docs.timescale.com/timescaledb/latest/overview/core-concepts/hypertables-and-chunks/hypertable-architecture/
        await RawTable.raw('ALTER TABLE stock_ticker_price DROP CONSTRAINT stock_ticker_price_pkey;')
        await RawTable.raw('ALTER TABLE stock_ticker_price ADD PRIMARY KEY (id, date);')

        await RawTable.raw("CREATE UNIQUE INDEX stock_ticker_price_sym_date_uq ON stock_ticker_price(symbol, date);")
        print(await RawTable.raw("SELECT create_hypertable('stock_ticker_price', 'date', chunk_time_interval => INTERVAL '1 day');"))

    async def create_option_price_hyptertable():
        await OptionPrice.create_table()

        # HACK: remove default id primary key, then recreate primary key with id and date
        # 1. Because piccolo forces us to create a primary key
        # 2. However any primary key or unique index in timescale db needs to include the partition column(trade_time)
        # https://docs.timescale.com/timescaledb/latest/overview/core-concepts/hypertables-and-chunks/hypertable-architecture/
        await RawTable.raw('ALTER TABLE option_price DROP CONSTRAINT option_price_pkey;')
        await RawTable.raw('ALTER TABLE option_price ADD PRIMARY KEY (id, trade_time);')

        await RawTable.raw(
            "CREATE UNIQUE INDEX option_price_basesym_exdate_strike_opt_typ_tradetime_uq ON option_price(base_symbol, expiration_date, strike_price, option_type, trade_time);")
        print(await RawTable.raw("SELECT create_hypertable('option_price', 'trade_time', chunk_time_interval => INTERVAL '1 day')"))

    async def run():
        await create_stock_ticker_table()
        await create_stock_ticker_price_hypertable()
        await create_option_price_hyptertable()

    async def run_backwards():
        await RawTable.raw('DROP TABLE IF EXISTS option_price')
        await RawTable.raw('DROP TABLE IF EXISTS stock_ticker_price')
        await RawTable.raw('DROP TABLE IF EXISTS stock_ticker')

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
