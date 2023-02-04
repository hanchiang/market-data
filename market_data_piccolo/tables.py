from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import BigSerial
from piccolo.columns.column_types import Date
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Numeric
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

class StockTicker(Table, tablename="stock_ticker"):
    symbol = Varchar(
        length=10,
        null=False,
        primary_key=True,
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
        target_column=None,
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
        target_column=None,
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


