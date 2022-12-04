import piccolo.table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager

from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Date, Timestamptz
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Numeric
from piccolo.columns.column_types import Varchar
from piccolo.table import Table

ID = "2022-12-04T17:05:53:969030"
VERSION = "0.99.0"
DESCRIPTION = "Add index"

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

    async def run():
        await StockTicker.create_index(columns=['symbol'])

        await StockTickerPrice.create_index(columns=['symbol', 'date'])

        await OptionPrice.create_index(columns=['base_symbol', 'trade_time'])
        await OptionPrice.create_index(columns=['base_symbol', 'option_type'])
        await OptionPrice.create_index(columns=['base_symbol', 'strike_price'])
        await OptionPrice.create_index(columns=['base_symbol', 'expiration_date'])

    async def run_backwards():
        await StockTicker.drop_index(columns=['symbol'])

        await StockTickerPrice.drop_index(columns=['symbol', 'date'])

        await OptionPrice.drop_index(columns=['base_symbol', 'trade_time'])
        await OptionPrice.drop_index(columns=['base_symbol', 'option_type'])
        await OptionPrice.drop_index(columns=['base_symbol', 'strike_price'])
        await OptionPrice.drop_index(columns=['base_symbol', 'expiration_date'])

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
