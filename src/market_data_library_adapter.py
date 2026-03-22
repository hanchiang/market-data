import dataclasses
import datetime
from typing import Any

from market_data_library.core.tradfi.barchart.type.barchart_type import (
    MostActiveOptions,
    OptionsExpiration,
    OptionsOIChange,
    OptionsPrice,
    StockPrice,
)


def serialize_payload(payload: Any) -> Any:
    if isinstance(payload, list):
        return [serialize_payload(item) for item in payload]

    if dataclasses.is_dataclass(payload):
        data = dataclasses.asdict(payload)
        data.pop("raw", None)
        return data

    return payload


def stock_price_to_db_row(stock_price: StockPrice) -> dict[str, Any]:
    return {
        "symbol": stock_price.symbol,
        "date": stock_price.date,
        "open_price": stock_price.open_price,
        "high_price": stock_price.high_price,
        "low_price": stock_price.low_price,
        "close_price": stock_price.close_price,
        "volume": stock_price.volume,
    }


def prepare_expiration_batches(expirations: OptionsExpiration) -> list[dict[str, Any]]:
    return [
        {
            "expiration_type": "weekly",
            "expiration_dates": expirations.weekly,
        },
        {
            "expiration_type": "monthly",
            "expiration_dates": expirations.monthly,
        },
    ]


def option_price_to_db_row(
    option_price: OptionsPrice, tz: datetime.tzinfo
) -> dict[str, Any]:
    raw = option_price.raw
    expiration_date = datetime.date.fromisoformat(raw.expirationDate)
    trade_time = datetime.datetime.fromtimestamp(raw.tradeTime, tz=tz)

    return {
        "symbol": raw.symbol,
        "base_symbol": raw.baseSymbol,
        "trade_time": trade_time,
        "option_type": raw.optionType,
        "strike_price": raw.strikePrice,
        "open_price": raw.openPrice,
        "high_price": raw.highPrice,
        "low_price": raw.lowPrice,
        "last_price": raw.lastPrice,
        "moneyness": raw.moneyness,
        "bid_price": raw.bidPrice,
        "midpoint": raw.midpoint,
        "ask_price": raw.askPrice,
        "volume": raw.volume,
        "open_interest": raw.openInterest,
        "volatility": raw.volatility,
        "expiration_date": expiration_date,
        "expiration_type": raw.expirationType,
        "average_volatility": raw.averageVolatility,
        "delta": raw.delta,
        "theta": raw.theta,
        "gamma": raw.gamma,
        "vega": raw.vega,
        "rho": raw.rho,
    }


SerializablePayload = list[
    StockPrice | OptionsPrice | MostActiveOptions | OptionsOIChange
] | OptionsExpiration
