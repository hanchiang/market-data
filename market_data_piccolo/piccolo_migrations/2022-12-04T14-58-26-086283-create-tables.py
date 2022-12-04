import piccolo.table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Date, Timestamptz
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Numeric
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table
import decimal


ID = "2022-12-04T14:58:26:086283"
VERSION = "0.99.0"
DESCRIPTION = "Create tables"

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

class StockTicker(Table):
    symbol = Varchar(10, primary_key=True)
    name = Varchar(255)

class StockTickerPrice(Table):
    symbol = ForeignKey(references=StockTicker, on_update=OnUpdate.cascade, on_delete=OnDelete.no_action)
    date = Date()
    open_price = Numeric(digits=stock_price_precision)
    high_price = Numeric(digits=stock_price_precision)
    low_price = Numeric(digits=stock_price_precision)
    close_price = Numeric(digits=stock_price_precision)
    volume = Integer()

class OptionPrice(Table):
    symbol: Varchar(100)
    base_symbol: ForeignKey(references=StockTicker, on_update=OnUpdate.cascade, on_delete=OnDelete.no_action)
    trade_time: Timestamptz()
    option_type: Varchar(4, help_text='put or call')
    strike_price: Numeric(digits=stock_price_precision)
    open_price: Numeric(digits=option_price_precision)
    high_price: Numeric(digits=option_price_precision)
    low_price: Numeric(digits=option_price_precision)
    last_price: Numeric(digits=option_price_precision)
    moneyness: Numeric(digits=option_aggregate_stat_precision)
    bid_price: Numeric(digits=option_price_precision)
    ask_price: Numeric(digits=option_price_precision)
    mid_price: Numeric(digits=option_price_precision)
    volume: Integer()
    open_interest: Integer()
    volatility: Numeric(digits=option_aggregate_stat_precision)
    expiration_date: Date()
    expiration_type: Varchar(6, help_text='weekly or monthly')
    average_volatility: Numeric(digits=option_aggregate_stat_precision)
    delta: Numeric(digits=option_greek_precision)
    theta: Numeric(digits=option_greek_precision)
    gamma: Numeric(digits=option_greek_precision)
    vega: Numeric(digits=option_greek_precision)
    rho: Numeric(digits=option_greek_precision)

async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="market_data_piccolo", description=DESCRIPTION
    )
    def create_stock_ticker(manager: MigrationManager):
        manager.add_table('StockTicker', tablename='stock_ticker')
        manager.add_column(
            table_class_name="StockTicker",
            tablename="stock_ticker",
            column_name="symbol",
            db_column_name="symbol",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "length": 10,
                "null": False,
                "primary_key": True,
                # "index": True,
                # "index_method": IndexMethod.btree,
            },
        )
        manager.add_column(
            table_class_name="StockTicker",
            tablename="stock_ticker",
            column_name="name",
            db_column_name="name",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "length": 255,
                "null": False,
            },
        )

    def create_stock_ticker_price(manager: MigrationManager):
        manager.add_table('StockTickerPrice', tablename='stock_ticker_price')
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="symbol",
            db_column_name="symbol",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "references": StockTicker,
                "on_delete": OnDelete.no_action,
                "on_update": OnUpdate.cascade,
                "target_column": None,
                "null": False,
                # "index": True,
                # "index_method": IndexMethod.btree
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="date",
            db_column_name="date",
            column_class_name="Date",
            column_class=Date,
            params={
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="open_price",
            db_column_name="open_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "default": decimal.Decimal("0"),
                "digits": stock_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice", tablename="stock_ticker_price",
            column_name="high_price",
            db_column_name="high_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "default": decimal.Decimal("0"),
                "digits": stock_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="low_price",
            db_column_name="low_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "default": decimal.Decimal("0"),
                "digits": stock_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="close_price",
            db_column_name="close_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": stock_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="volume",
            db_column_name="volume",
            column_class_name="Integer",
            column_class=Integer,
            params={
                "null": False,
            },
        )

    def create_option_price(manager: MigrationManager):
        manager.add_table('OptionPrice', tablename='option_price')
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="symbol",
            db_column_name="symbol",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "length": 100,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="base_symbol",
            db_column_name="base_symbol",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "references": StockTicker,
                "on_delete": OnDelete.no_action,
                "on_update": OnUpdate.cascade,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="trade_time",
            db_column_name="trade_time",
            column_class_name="Timestamptz",
            column_class=Timestamptz,
            params={
                "null": False,
                # "index": True,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="option_type",
            db_column_name="option_type",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "length": 4,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="strike_price",
            db_column_name="strike_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": stock_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="open_price",
            db_column_name="open_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="high_price",
            db_column_name="high_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="low_price",
            db_column_name="low_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="last_price",
            db_column_name="last_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="moneyness",
            db_column_name="moneyness",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_aggregate_stat_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="bid_price",
            db_column_name="bid_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="ask_price",
            db_column_name="ask_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="mid_price",
            db_column_name="mid_price",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_price_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="volume",
            db_column_name="volume",
            column_class_name="Integer",
            column_class=Integer,
            params={
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="StockTickerPrice",
            tablename="stock_ticker_price",
            column_name="open_interest",
            db_column_name="open_interest",
            column_class_name="Integer",
            column_class=Integer,
            params={
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="volatility",
            db_column_name="volatility",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_aggregate_stat_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="expiration_date",
            db_column_name="expiration_date",
            column_class_name="Date",
            column_class=Date,
            params={
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="expiration_type",
            db_column_name="expiration_type",
            column_class_name="Varchar",
            column_class=Varchar,
            params={
                "length": 6,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="average_volatility",
            db_column_name="average_volatility",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_aggregate_stat_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="delta",
            db_column_name="delta",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_greek_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="theta",
            db_column_name="theta",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_greek_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="gamma",
            db_column_name="gamma",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_greek_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="vega",
            db_column_name="vega",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_greek_precision,
                "null": False,
            },
        )
        manager.add_column(
            table_class_name="OptionPrice",
            tablename="option_price",
            column_name="rho",
            db_column_name="rho",
            column_class_name="Numeric",
            column_class=Numeric,
            params={
                "digits": option_greek_precision,
                "null": False,
            },
        )
    def run():
        create_stock_ticker(manager)
        create_stock_ticker_price(manager)
        create_option_price(manager)

        # For some reason, columns for OptionPrice table are not created if tables are created with piccolo.table.create_db_tables_sync
        # piccolo.table.create_db_tables_sync(StockTicker, StockTickerPrice, OptionPrice)

    def run_backwards():
        # For some reason, columns tables class name can't find found when tables are dropped with manager
        piccolo.table.drop_db_tables_sync(StockTicker, StockTickerPrice, OptionPrice)

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
