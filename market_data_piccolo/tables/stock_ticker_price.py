
from piccolo.columns import BigSerial, ForeignKey, OnDelete, OnUpdate, Date, Numeric, Integer, Timestamptz
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table

from market_data_piccolo.tables.common import stock_price_precision
from market_data_piccolo.tables.stock_ticker import StockTicker

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
    created_at = Timestamptz(
        null=False,
        primary_key=False,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        db_column_name=None,
        secret=False
    )