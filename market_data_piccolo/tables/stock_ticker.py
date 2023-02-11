
from piccolo.columns import Varchar, BigSerial, Timestamptz
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


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