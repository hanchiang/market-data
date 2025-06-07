import datetime
from zoneinfo import ZoneInfo

# Time zone constant for New York (US market)
ny_tz = ZoneInfo("America/New_York")

# Market hours constants
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 15


def time_now() -> datetime.datetime:
    """
    Get the current time in New York timezone.

    Returns:
        datetime.datetime: Current datetime in NY timezone
    """
    return datetime.datetime.now().astimezone(tz=ny_tz)


def has_market_opened() -> bool:
    """
    Check if the US market has opened for the day.
    Market opens at 9:30 AM Eastern Time.

    Returns:
        bool: True if market is open, False otherwise
    """
    ny_now = time_now()
    return (ny_now.hour > MARKET_OPEN_HOUR or
            (ny_now.hour == MARKET_OPEN_HOUR and ny_now.minute >= MARKET_OPEN_MINUTE))


def has_market_closed() -> bool:
    """
    Check if the US market has closed for the day.
    Market closes at 4:15 PM Eastern Time.

    Returns:
        bool: True if market has closed, False otherwise
    """
    ny_now = time_now()
    return ny_now.hour > MARKET_CLOSE_HOUR or ny_now.hour == MARKET_CLOSE_HOUR and ny_now.minute >= MARKET_CLOSE_MINUTE


def get_most_recent_trading_day() -> datetime.datetime:
    """
    Get the most recent trading day.

    If today's market has opened, return today's date.
    If today's market has not opened yet, return yesterday's date.
    Handle weekends by returning Friday for Saturday/Sunday.

    Returns:
        datetime.datetime: The most recent trading day as a datetime object
    """
    ny_now = time_now()
    day_of_week = ny_now.weekday()  # Monday = 0, Sunday = 6
    days_to_subtract = 0

    # If market hasn't opened today, use previous day
    if not has_market_opened():
        days_to_subtract += 1

    # Weekend handling
    if day_of_week == 5:  # Saturday
        days_to_subtract = 1
    elif day_of_week == 6:  # Sunday
        days_to_subtract = 2

    # Adjust for Monday mornings before market opens
    if day_of_week == 0 and not has_market_opened():
        days_to_subtract = 3

    return ny_now - datetime.timedelta(days=days_to_subtract)



def get_current_utc_time() -> datetime.datetime:
    """Get current UTC datetime."""
    return datetime.datetime.now().astimezone(datetime.timezone.utc)


def convert_to_utc(dt: datetime.datetime) -> datetime.datetime:
    """Convert a datetime to UTC timezone."""
    if dt.tzinfo is None:
        # If the datetime is naive, assume it is in UTC
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("UTC"))
