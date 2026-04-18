import dataclasses
import datetime
from collections.abc import Mapping
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


def _get_raw_option_value(raw: Any, field: str) -> Any:
    if isinstance(raw, Mapping):
        if field in raw:
            return raw[field]
    elif hasattr(raw, field):
        return getattr(raw, field)

    raise KeyError(f"Option payload raw is missing required field: {field}")


def _resolve_option_trade_time(
    raw: Any,
    tz: datetime.tzinfo,
    default_trade_time: datetime.datetime | None,
) -> datetime.datetime:
    raw_trade_time = _get_raw_option_value(raw, "tradeTime")

    try:
        return datetime.datetime.fromtimestamp(raw_trade_time, tz=tz)
    except (OSError, OverflowError, TypeError, ValueError):
        if default_trade_time is not None:
            return default_trade_time.astimezone(tz)

        raise ValueError(f"Invalid option tradeTime: {raw_trade_time}") from None


def option_price_to_db_row(
    option_price: OptionsPrice,
    tz: datetime.tzinfo,
    default_trade_time: datetime.datetime | None = None,
) -> dict[str, Any]:
    raw = option_price.raw
    expiration_date = datetime.date.fromisoformat(
        _get_raw_option_value(raw, "expirationDate")
    )
    trade_time = _resolve_option_trade_time(raw, tz, default_trade_time)

    return {
        "symbol": _get_raw_option_value(raw, "symbol"),
        "base_symbol": _get_raw_option_value(raw, "baseSymbol"),
        "trade_time": trade_time,
        "option_type": _get_raw_option_value(raw, "optionType"),
        "strike_price": _get_raw_option_value(raw, "strikePrice"),
        "open_price": _get_raw_option_value(raw, "openPrice"),
        "high_price": _get_raw_option_value(raw, "highPrice"),
        "low_price": _get_raw_option_value(raw, "lowPrice"),
        "last_price": _get_raw_option_value(raw, "lastPrice"),
        "moneyness": _get_raw_option_value(raw, "moneyness"),
        "bid_price": _get_raw_option_value(raw, "bidPrice"),
        "midpoint": _get_raw_option_value(raw, "midpoint"),
        "ask_price": _get_raw_option_value(raw, "askPrice"),
        "volume": _get_raw_option_value(raw, "volume"),
        "open_interest": _get_raw_option_value(raw, "openInterest"),
        "volatility": _get_raw_option_value(raw, "volatility"),
        "expiration_date": expiration_date,
        "expiration_type": _get_raw_option_value(raw, "expirationType"),
        "average_volatility": _get_raw_option_value(raw, "averageVolatility"),
        "delta": _get_raw_option_value(raw, "delta"),
        "theta": _get_raw_option_value(raw, "theta"),
        "gamma": _get_raw_option_value(raw, "gamma"),
        "vega": _get_raw_option_value(raw, "vega"),
        "rho": _get_raw_option_value(raw, "rho"),
    }


SerializablePayload = list[
    StockPrice | OptionsPrice | MostActiveOptions | OptionsOIChange
] | OptionsExpiration
