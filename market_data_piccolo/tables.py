from piccolo.table import Table
from piccolo.columns import Varchar, ForeignKey, OnDelete, OnUpdate, Date, Numeric, Integer, Timestamptz

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