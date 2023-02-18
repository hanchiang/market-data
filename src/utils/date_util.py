import datetime
import pytz

ny_tz = pytz.timezone('America/New_York')

def time_now():
    return datetime.datetime.now().astimezone(tz=ny_tz)

# market hours: 9.30am - 4pm. Some ETF close at 4.15pm
def has_market_opened():
    ny_now = time_now()
    return ny_now.hour > 9 or (ny_now.hour == 9 and ny_now.minute > 30)

def has_market_closed():
    ny_now = time_now()
    return ny_now.hour > 16 or (ny_now.hour == 16 and ny_now.minute > 15)

def get_most_recent_trading_day() -> datetime.datetime:
    ny_now = time_now()
    # Monday == 0, Sunday == 6
    day_of_week = ny_now.weekday()
    days_to_subtract = 0

    if not has_market_closed():
        days_to_subtract += 1

    if day_of_week == 5:
        days_to_subtract = 1
    elif day_of_week == 6:
        days_to_subtract = 2

    return ny_now - datetime.timedelta(days=days_to_subtract)